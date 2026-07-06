<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '../stores/auth'
import { useTasks } from '../stores/tasks'
import TaskItem from '../components/TaskItem.vue'

const auth = useAuth()
const tasks = useTasks()

const showAll = ref(false)
const title = ref('')
const description = ref('')

// DEMO (issue 2 & 4): `tasks.all` holds every task from every user (the store was
// filled by the over-fetching API). Non-admins just get a client-side filter —
// the other users' data, incl. internal_notes, is still in memory.
const visible = computed(() => {
  if (auth.isAdmin || showAll.value) return tasks.all
  return tasks.all.filter(
    (t) => t.owner_id === auth.user.id || t.assignee_id === auth.user.id
  )
})

onMounted(() => tasks.load())

async function add() {
  if (!title.value.trim()) return
  await tasks.create({ title: title.value, description: description.value, status: 'todo' })
  title.value = ''
  description.value = ''
}
</script>

<template>
  <div class="container">
    <div class="card">
      <h2 style="margin-top: 0">New task</h2>
      <label>Title</label>
      <input v-model="title" placeholder="Task title" />
      <label>Description (supports rich text)</label>
      <textarea v-model="description" placeholder="Description…"></textarea>
      <div class="row" style="margin-top: 12px">
        <button @click="add">Add task</button>
        <div class="spacer"></div>
        <label class="row muted" style="margin: 0; gap: 6px">
          <input type="checkbox" v-model="showAll" style="width: auto" /> show all users' tasks
        </label>
      </div>
    </div>

    <TaskItem
      v-for="t in visible"
      :key="t.id"
      :task="t"
      @delete="tasks.remove"
      @advance="({ id, status }) => tasks.setStatus(id, status)"
    />
    <p class="muted" v-if="!visible.length">No tasks.</p>
  </div>
</template>
