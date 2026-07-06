import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    // allow importing the shared stylesheet that lives outside this folder
    fs: { allow: ['../..'] },
  },
})
