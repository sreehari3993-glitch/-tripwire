import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    proxy: {
      '/auth': 'http://127.0.0.1:8000',
      '/dashboard': 'http://127.0.0.1:8000',
      '/students': 'http://127.0.0.1:8000',
      '/alerts': 'http://127.0.0.1:8000',
      '/interventions': 'http://127.0.0.1:8000',
      '/analytics': 'http://127.0.0.1:8000',
      '/demo': 'http://127.0.0.1:8000',
      '/api': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    }
  },
})
