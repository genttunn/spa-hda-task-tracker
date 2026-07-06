<script setup>
import { computed } from 'vue'
import { useAuth } from '../stores/auth'
import { priorityLabel } from '../lib/priority'

const props = defineProps({ task: Object })
const emit = defineEmits(['delete', 'advance'])
const auth = useAuth()

// DEMO (issue 5): priority is computed here in the browser from the shipped algorithm.
const label = computed(() => priorityLabel(props.task))

const NEXT = { todo: 'in_progress', in_progress: 'blocked', blocked: 'done', done: 'todo' }
</script>

<template>
  <div class="task">
    <span class="badge" :class="label">{{ label }}</span>
    <div class="body">
      <h3>{{ task.title }}</h3>
      <!-- DEMO (issue 1): description is rendered as raw HTML so "rich text" works.
           A crafted description executes as script — this is the stored-XSS sink. -->
      <div class="desc" v-html="task.description"></div>
      <div class="meta">
        <span class="status">status: {{ task.status }}</span>
        <span>owner #{{ task.owner_id }}</span>
        <span>assignee: {{ task.assignee_id ?? '—' }}</span>
        <span>created {{ task.created_at }}</span>
      </div>
    </div>
    <div class="row" style="gap: 6px">
      <button class="secondary" @click="emit('advance', { id: task.id, status: NEXT[task.status] })">
        → {{ NEXT[task.status] }}
      </button>
      <!-- DEMO (issue 4): the Delete button is only hidden for non-admins on the
           client. The server enforces nothing, so re-enabling it in DevTools works. -->
      <button v-if="auth.isAdmin" class="danger" @click="emit('delete', task.id)">Delete</button>
    </div>
  </div>
</template>
