import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import TasksView from '../views/TasksView.vue'

// NOTE: static import — AdminView is compiled into the main JS bundle for ALL users,
// regardless of their role. The route guard below prevents navigation, but the component
// code (including admin UI logic) is present in the downloaded JavaScript.
// Open DevTools > Network > JS bundle and search for "AdminView" to confirm.
import AdminView from '../views/AdminView.vue'

const routes = [
  { path: '/', redirect: '/tasks' },
  { path: '/login', component: LoginView },
  { path: '/tasks', component: TasksView, meta: { requiresAuth: true } },
  { path: '/admin', component: AdminView, meta: { requiresAuth: true, requiresAdmin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  // useAuthStore() called inside the callback, not at module scope.
  // Pinia must be installed (app.use(createPinia())) before this runs.
  // Since beforeEach fires on navigation (after app setup), this is safe.
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.token) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/tasks')
  } else {
    next()
  }
})

export default router
