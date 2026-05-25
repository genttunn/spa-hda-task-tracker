import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import apiClient from '../api/client'

function decodeJwtPayload(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]))
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAdmin = computed(() => user.value?.is_admin === true)

  async function login(username, password) {
    const response = await apiClient.post('/api/auth/login', { username, password })
    const { access_token, user: userData } = response.data

    token.value = access_token
    user.value = userData
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))

    // Demo hook: JWT payload is fully readable by JavaScript — no server round-trip needed.
    // This is visible to any XSS attacker who can run JS in this page's context.
    console.log('[SPA Demo] JWT payload (decoded):', decodeJwtPayload(access_token))
    console.log('[SPA Demo] Token stored in localStorage — readable via localStorage.getItem("access_token")')
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    // Note: the token is still cryptographically valid on the server until it expires.
    // There is no server-side session to invalidate — logging out here is client-only.
  }

  return { token, user, isAdmin, login, logout }
})
