import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Khi chạy trong Docker, trỏ tới http://gateway-service:8000; khi chạy local, trỏ tới http://localhost:8000
const API_TARGET = process.env.VITE_API_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Lắng nghe trên tất cả interface (Mobile, LAN, Tunnel)
    port: 5173,
    allowedHosts: true, // Cho phép tất cả tunnel host (Cloudflare Tunnel, Ngrok, 4G/5G) truy cập không bị chặn
    proxy: {
      // Proxy tất cả request /api → API Gateway
      '/api': {
        target: API_TARGET,
        changeOrigin: true,
      },
      // Proxy file audio output
      '/output': {
        target: API_TARGET,
        changeOrigin: true,
      }
    }
  }
})
