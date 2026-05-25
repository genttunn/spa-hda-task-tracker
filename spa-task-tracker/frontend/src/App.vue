<template>
  <div>
    <nav>
      <RouterLink to="/login">Login</RouterLink>
      <template v-if="authStore.token">
        <RouterLink to="/tasks">Tasks</RouterLink>
        <!-- Admin link hidden for non-admins — but AdminView is still in the JS bundle.
             A user can navigate to /admin directly; the route guard will redirect them.
             However, if localStorage is manually edited to set is_admin: true, the guard
             passes and AdminView renders — the API then returns 403. Client-side guards
             are UX, not security. -->
        <RouterLink v-if="authStore.isAdmin" to="/admin">Admin</RouterLink>
        <button @click="handleLogout">Logout</button>
      </template>
    </nav>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()
const router = useRouter()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
body { margin: 0; font-family: sans-serif; }
nav { background: #343a40; padding: 12px 24px; display: flex; gap: 16px; align-items: center; }
nav a { color: #adb5bd; text-decoration: none; }
nav a.router-link-active { color: white; }
nav button { margin-left: auto; background: transparent; border: 1px solid #adb5bd; color: #adb5bd; padding: 4px 12px; cursor: pointer; border-radius: 4px; }
nav button:hover { color: white; border-color: white; }
main { padding: 0 24px; }
</style>
