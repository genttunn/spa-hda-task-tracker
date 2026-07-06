import { defineStore } from 'pinia'
import api from '../api'

// DEMO (issue 2 & 4): the store caches EVERY task returned by the over-fetching
// API — including tasks the current user doesn't own and hidden fields like
// internal_notes. The UI filters what's shown, but all of it sits in browser
// memory and is inspectable via Vue DevTools / the Network tab.
export const useTasks = defineStore('tasks', {
  state: () => ({ all: [] }),
  actions: {
    async load() {
      const { data } = await api.get('/api/tasks')
      this.all = data
    },
    async create(payload) {
      const { data } = await api.post('/api/tasks', payload)
      this.all.push(data)
    },
    async remove(id) {
      await api.delete(`/api/tasks/${id}`)
      this.all = this.all.filter((t) => t.id !== id)
    },
    async setStatus(id, status) {
      const { data } = await api.put(`/api/tasks/${id}`, { status })
      const i = this.all.findIndex((t) => t.id === id)
      if (i >= 0) this.all[i] = data
    },
  },
})
