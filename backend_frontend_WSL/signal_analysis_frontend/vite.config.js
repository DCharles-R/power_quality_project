import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Redirige cualquier petición que comience con /api a tu backend de Django
      '/api': {
        target: 'http://127.0.0.1:8000', // La dirección de tu servidor Django
        changeOrigin: true,
        secure: false, // Descomenta si tu backend no usa HTTPS
      }
    }
  }
})