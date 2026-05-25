<template>
  <div class="admin-page">
    <div class="demo-banner">
      ⚠ <strong>[SPA Demo]</strong> This component (AdminView) exists in the JS bundle for ALL
      users — including non-admins. Open DevTools → Network → JS bundle and search for "AdminView"
      or "admin" to confirm. The route guard prevents navigation, but the code is already
      downloaded.
    </div>

    <h1>Admin — All Tasks</h1>

    <section class="debug-section">
      <h2>Server view of your token (<code>/api/debug/me</code>)</h2>
      <pre v-if="debugInfo">{{ JSON.stringify(debugInfo, null, 2) }}</pre>
      <p v-else>Loading…</p>
    </section>

    <section>
      <h2>All users' tasks</h2>
      <p v-if="allTasks.length === 0">No tasks found.</p>
      <table v-else>
        <thead>
          <tr>
            <th>Owner</th>
            <th>Title</th>
            <th>Notes (unsafe)</th>
            <th>Done</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in allTasks" :key="task.id">
            <td>{{ task.owner_username }}</td>
            <td>{{ task.title }}</td>
            <!-- v-html here too — same XSS surface as TasksView -->
            <td v-html="task.notes || ''"></td>
            <td>{{ task.completed ? '✓' : '' }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import apiClient from '../api/client'

const allTasks = ref([])
const debugInfo = ref(null)

onMounted(async () => {
  const [tasksRes, debugRes] = await Promise.all([
    apiClient.get('/api/admin/tasks'),
    apiClient.get('/api/auth/debug/me'),
  ])
  allTasks.value = tasksRes.data
  debugInfo.value = debugRes.data
})
</script>

<style scoped>
.admin-page { max-width: 800px; margin: 40px auto; font-family: sans-serif; }
.demo-banner { background: #f8d7da; border: 1px solid #f5c6cb; padding: 12px; border-radius: 4px; margin-bottom: 24px; }
.debug-section { background: #f8f9fa; padding: 12px; border-radius: 4px; margin-bottom: 24px; }
pre { font-size: 12px; white-space: pre-wrap; word-break: break-all; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
th { background: #f8f9fa; }
</style>
