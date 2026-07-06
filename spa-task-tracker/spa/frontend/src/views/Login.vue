<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../stores/auth'

const auth = useAuth()
const router = useRouter()
const username = ref('alice')
const password = ref('alice123')
const error = ref('')

async function submit() {
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    router.push('/tasks')
  } catch (e) {
    error.value = 'Invalid credentials'
  }
}
</script>

<template>
  <div class="login-wrap">
    <div class="card">
      <h2 style="margin-top: 0">Sign in</h2>
      <form @submit.prevent="submit">
        <label>Username</label>
        <input v-model="username" autocomplete="username" />
        <label>Password</label>
        <input v-model="password" type="password" autocomplete="current-password" />
        <div class="error" v-if="error">{{ error }}</div>
        <button style="margin-top: 16px; width: 100%">Sign in</button>
      </form>
      <p class="hint">Try admin/admin123 · alice/alice123 · bob/bob123</p>
    </div>
  </div>
</template>
