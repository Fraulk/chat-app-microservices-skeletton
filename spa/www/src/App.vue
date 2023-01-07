<script setup>
import { RouterLink, RouterView } from "vue-router";
import { useUser } from "./stores/user";
import Home from "../assets/icons/Home.vue";
import Chat from "../assets/icons/Chat.vue";
import LogOut from "../assets/icons/LogOut.vue";
import Register from "../assets/icons/Register.vue";

const { token, isLoggedIn, logOut } = useUser();
</script>

<template>
  <div class="App">
    <div class="content">
    <!-- {{ isLoggedIn }} -->
    <!-- {{ token }} -->
      <header>
        <div class="wrapper">
          <nav>
            <RouterLink to="/"><Home /></RouterLink>
            <template v-if="isLoggedIn">
              <span @click="logOut"><LogOut /></span>
              <RouterLink to="/chat"><Chat /></RouterLink>
            </template>
            <RouterLink v-else to="/register"><Register /></RouterLink>
          </nav>
        </div>
      </header>

      <!--- https://vuejs.org/guide/built-ins/suspense.html#combining-with-other-components --> 
      <RouterView v-slot="{ Component }">
        <template v-if="Component">
          <Suspense>
            <!-- main content -->
            <component :is="Component"></component>

            <!-- loading state -->
            <template #fallback> Loading... </template>
          </Suspense>
        </template>
      </RouterView>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import "./app.scss";
</style>