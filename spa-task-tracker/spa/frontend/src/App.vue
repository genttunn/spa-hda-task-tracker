<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from './stores/auth'

const auth = useAuth()
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="app-header">
    <div class="brand">TaskTracker <span class="tag">SPA · Vue</span></div>
    <div class="row" v-if="auth.isAuthed">
      <span class="user">{{ auth.user.username }} ({{ auth.user.role }})</span>
      <button class="secondary" @click="logout">Log out</button>
    </div>
  </header>
  <router-view />
</template>
