import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// No proxy configured intentionally — Flask runs on :5000, Vite on :5173.
// Keeping them as separate origins makes CORS headers visible in DevTools.
// If you added a server.proxy here, all requests would share the Vite origin
// and Flask would never emit CORS headers, defeating the demo.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
  },
})
