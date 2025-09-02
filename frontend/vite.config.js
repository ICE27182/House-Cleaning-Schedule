import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // When running `npm run dev`, Vite will proxy /api/... to the Flask server
    proxy: {
      '/api': {
        target: 'http://localhost:80',
        // changeOrigin: true,          // necessary for some hosts
        // rewrite: (path) => path,     // keep the /api prefix (or strip it if your Flask app expects it removed)
      },
    },
  },
})
