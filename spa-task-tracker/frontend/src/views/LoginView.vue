<template>
  <div class="login-page">
    <h1>Task Tracker — Login</h1>

    <form @submit.prevent="handleLogin">
      <div>
        <label>Username</label>
        <input v-model="username" type="text" autocomplete="username" required />
      </div>
      <div>
        <label>Password</label>
        <input v-model="password" type="password" autocomplete="current-password" required />
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <button type="submit" :disabled="loading">{{ loading ? 'Logging in…' : 'Login' }}</button>
    </form>

    <p>No account? <a href="#" @click.prevent="handleRegister">Register</a></p>

    <!-- Demo: JWT visible in localStorage after login -->
    <div v-if="authStore.token" class="debug-panel">
      <strong>[SPA Demo] JWT stored in localStorage:</strong>
      <pre>{{ authStore.token }}</pre>
      <small>Open DevTools → Application → Local Storage to see this at rest.</small>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '../api/client'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    router.push('/tasks')
  } catch (e) {
    error.value = e.response?.data?.error || 'Login failed'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  loading.value = true
  try {
    await apiClient.post('/api/auth/register', {
      username: username.value,
      password: password.value,
    })
    await authStore.login(username.value, password.value)
    router.push('/tasks')
  } catch (e) {
    error.value = e.response?.data?.error || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page { max-width: 400px; margin: 60px auto; font-family: sans-serif; }
form div { margin-bottom: 12px; }
label { display: block; margin-bottom: 4px; }
input { width: 100%; padding: 6px; box-sizing: border-box; }
button { padding: 8px 16px; cursor: pointer; }
.error { color: red; }
.debug-panel { margin-top: 24px; background: #fff3cd; padding: 12px; border: 1px solid #ffc107; border-radius: 4px; word-break: break-all; }
pre { white-space: pre-wrap; font-size: 11px; }
</style>
