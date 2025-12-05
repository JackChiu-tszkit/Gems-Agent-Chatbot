import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,  // Use port 3000 to avoid configuration conflicts
    headers: {
      // Allow popups for Google Sign-In to communicate with parent window
      'Cross-Origin-Opener-Policy': 'same-origin-allow-popups',
      // COEP can interfere with Google Sign-In, remove if not needed
      // 'Cross-Origin-Embedder-Policy': 'require-corp',
    },
  },
})
