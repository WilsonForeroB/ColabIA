import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuración de Vite.
// El proxy redirige cualquier petición a /api hacia el backend FastAPI
// (localhost:8000). Así el frontend llama a rutas relativas (/api/chat)
// y el navegador no se queja de CORS durante el desarrollo.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
