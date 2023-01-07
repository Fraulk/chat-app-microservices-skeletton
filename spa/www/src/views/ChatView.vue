<script setup>
import { useWebSocket } from "@vueuse/core";
import { ref } from "vue";
import { useUser } from "../stores/user";
import { useCookies } from "@vueuse/integrations/useCookies";
import Send from "../../assets/icons/Send.vue";

const { token } = useUser();
const cookies = useCookies(["session"]);
console.log(token.value);
cookies.set("session", token.value);

const { send } = useWebSocket("ws://localhost/chat/ws", {
  onMessage: (_, event) => {
    console.log(event);
    const data = JSON.parse(event.data);
    console.log(data);
    if (data.type == "reaction")
      messages.value[messages.value.findIndex(item => item.id == data.id)].reaction = data.reaction
    else
      messages.value.push(data);
  },
});

const messages = ref([]);

const isAddingReaction = ref({});

const addReaction = ref("");

const payload = ref("");

function sendMessage() {
  const ok = send(JSON.stringify({ message: payload.value }));
  if (ok) {
    payload.value = "";
  }
}

const inputReaction = (id) => {
  isAddingReaction.value = {status: true, id}
}

const sendNewReaction = (id) => {
  isAddingReaction.value = {status: false, id: ""}
  const regexpEmojiPresentation = /\p{Emoji_Presentation}/u;
  let reaction = addReaction.value.match(regexpEmojiPresentation)
  if (reaction == null) return
  send(JSON.stringify({ reaction: reaction[0], id}))
}

const sendExistentReaction = (id, reaction) => send(JSON.stringify({ reaction, id}))

</script>

<template>
  <div class="ChatView">
    <div class="messages">
      <article class="message" :key="index" v-for="(message, index) in messages">
        <div class="username">
          <span>{{ message.username ?? "Anonymous" }}</span> said at
          {{ new Date(message.date).toLocaleDateString() }}:
        </div>
        {{ message.message }}
        <div class="reactions">
          <div v-for="(react, i) in message.reaction" :key="i" @click="sendExistentReaction(message.id, react.reaction)" class="reaction">
            {{ String.fromCodePoint(isNaN(react.reaction) ? "0x" + react.reaction.codePointAt(0).toString(16) : react.reaction) }}: {{ react.client.length }}
          </div>
          <div class="new-reaction" @click="inputReaction(message.id)">+</div>
          <input
            type="text"
            v-if="isAddingReaction.status == true && isAddingReaction.id == message.id"
            v-model="addReaction"
            @keypress.enter="sendNewReaction(message.id)"
          >
          <div
            v-if="isAddingReaction.status == true && isAddingReaction.id == message.id"
            class="reaction"
            @click="sendNewReaction(message.id)"
          >
            Send
          </div>
        </div>
      </article>
    </div>
    <div class="send-message">
      <input
        type="text"
        v-model="payload"
        @keypress.enter="sendMessage"
        placeholder="Message the world"
      />
      <div class="separator"></div>
      <Send @click="sendMessage">Send</Send>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "../ChatView.scss";
</style>
