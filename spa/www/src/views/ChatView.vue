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
    console.log(event)
    const data = event.data;
    console.log(data);
    messages.value.push(data);
  },
});

const messages = ref([
  {
    type: "new_message",
    id: "1332154648",
    client: "LeBGdu90",
    message: "Hello world!",
    reaction: [
      {
        reaction: "poop",
        client: ["<client_id_1>", "<client_id_2>"],
      },
    ],
    date: new Date(),
  },
  {
    type: "new_message",
    id: "133212158",
    client: "xXDark_SasukeXx",
    message: "AAAA AAAAA A AAAAAAAA AAAAAA AAAA AA AAAAAA",
    reaction: [
      {
        reaction: "poop",
        client: ["<client_id_1>", "<client_id_2>"],
      },
    ],
    date: new Date(),
  },
]);

const payload = ref("");

function sendMessage() {
  const ok = send(JSON.stringify(payload.value));
  if (ok) {
    payload.value = "";
  }
}
</script>

<template>
  <div class="ChatView">
    <div class="messages">
      <div class="message" :key="index" v-for="(message, index) in messages">
        <div class="username"><span>{{ message.client }}</span> said at {{message.date.toLocaleDateString()}}:</div> {{ message.message }}
      </div>
    </div>
    <div class="send-message">
      <input type="text" v-model="payload" @keypress.enter="sendMessage" placeholder="Message the world" />
      <div class="separator"></div>
      <Send @click="sendMessage">Send</Send>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import '../ChatView.scss'
</style>