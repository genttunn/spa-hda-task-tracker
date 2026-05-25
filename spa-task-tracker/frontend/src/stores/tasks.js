import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient from '../api/client'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref([])

  async function fetchTasks() {
    const response = await apiClient.get('/api/tasks')
    tasks.value = response.data
  }

  async function createTask(title, notes) {
    const response = await apiClient.post('/api/tasks', { title, notes })
    tasks.value.push(response.data)
  }

  async function updateTask(id, payload) {
    const index = tasks.value.findIndex((t) => t.id === id)
    if (index !== -1) {
      // Optimistic update: mutate local state before the server confirms.
      // Intentionally not rolling back on error — demo of state desync.
      // If the server rejects (e.g. task deleted server-side), the UI still shows the old value.
      Object.assign(tasks.value[index], payload)
    }
    await apiClient.put(`/api/tasks/${id}`, payload)
  }

  async function deleteTask(id) {
    await apiClient.delete(`/api/tasks/${id}`)
    tasks.value = tasks.value.filter((t) => t.id !== id)
  }

  return { tasks, fetchTasks, createTask, updateTask, deleteTask }
})
