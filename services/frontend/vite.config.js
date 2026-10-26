import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',    // Lắng nghe trên tất cả interface → điện thoại cùng WiFi truy cập được
    port: 5173,
    proxy: {
      // Proxy tất cả request /api → FastAPI backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Proxy file audio output
      '/output': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
