<template>
  <div class="tasks-page">
    <h1>My Tasks</h1>

    <!-- Create task form -->
    <form @submit.prevent="handleCreate" class="create-form">
      <input v-model="newTitle" placeholder="Task title" required />
      <input v-model="newNotes" placeholder="Notes (unsafe — renders HTML)" />
      <button type="submit">Add Task</button>
    </form>
    <small class="warning">
      ⚠ Notes field renders raw HTML via v-html. XSS demo payload:<br />
      <code>&lt;img src=x onerror="alert(localStorage.getItem('access_token'))"&gt;</code>
    </small>

    <p v-if="tasksStore.tasks.length === 0">No tasks yet.</p>

    <ul class="task-list">
      <li v-for="task in tasksStore.tasks" :key="task.id" :class="{ completed: task.completed }">
        <div class="task-header">
          <strong>{{ task.title }}</strong>
          <div class="task-actions">
            <button @click="toggleComplete(task)">
              {{ task.completed ? 'Undo' : 'Complete' }}
            </button>
            <button @click="tasksStore.deleteTask(task.id)" class="delete">Delete</button>
          </div>
        </div>
        <!-- DEMO HOOK: v-html renders raw HTML — XSS surface.
             Payload that works: <img src=x onerror="alert(localStorage.getItem('access_token'))">
             Note: <script>alert(1)</script> does NOT execute via v-html in modern browsers.
             Use img/onerror or other event-handler injection instead. -->
        <div v-if="task.notes" class="task-notes" v-html="task.notes"></div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useTasksStore } from '../stores/tasks'

const tasksStore = useTasksStore()
const newTitle = ref('')
const newNotes = ref('')

onMounted(() => tasksStore.fetchTasks())

async function handleCreate() {
  if (!newTitle.value.trim()) return
  await tasksStore.createTask(newTitle.value.trim(), newNotes.value)
  newTitle.value = ''
  newNotes.value = ''
}

function toggleComplete(task) {
  tasksStore.updateTask(task.id, { completed: !task.completed })
}
</script>

<style scoped>
.tasks-page { max-width: 600px; margin: 40px auto; font-family: sans-serif; }
.create-form { display: flex; gap: 8px; margin-bottom: 8px; }
.create-form input { flex: 1; padding: 6px; }
.warning { display: block; margin-bottom: 20px; color: #856404; background: #fff3cd; padding: 8px; border-radius: 4px; }
code { font-size: 11px; word-break: break-all; }
.task-list { list-style: none; padding: 0; }
.task-list li { padding: 12px; border: 1px solid #ddd; margin-bottom: 8px; border-radius: 4px; }
.task-list li.completed { opacity: 0.5; }
.task-header { display: flex; justify-content: space-between; align-items: center; }
.task-actions { display: flex; gap: 8px; }
.task-notes { margin-top: 8px; font-size: 13px; color: #444; border-top: 1px solid #eee; padding-top: 8px; }
button.delete { color: red; }
</style>
