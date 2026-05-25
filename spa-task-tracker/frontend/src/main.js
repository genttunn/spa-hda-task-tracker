import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)

// Pinia must be installed before the router, because the router's beforeEach
// guard calls useAuthStore() — which requires Pinia to be active.
app.use(createPinia())
app.use(router)

app.mount('#app')
