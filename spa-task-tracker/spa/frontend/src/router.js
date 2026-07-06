import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from './stores/auth'
import Login from './views/Login.vue'
import Tasks from './views/Tasks.vue'

const routes = [
  { path: '/', redirect: '/tasks' },
  { path: '/login', component: Login },
  { path: '/tasks', component: Tasks, meta: { requiresAuth: true } },
]

const router = createRouter({ history: createWebHistory(), routes })

// DEMO (issue 4): route guarding happens entirely client-side. It's a UX gate,
// not a security control — the real protection must live on the server.
router.beforeEach((to) => {
  const auth = useAuth()
  if (to.meta.requiresAuth && !auth.isAuthed) return '/login'
  if (to.path === '/login' && auth.isAuthed) return '/tasks'
})

export default router
