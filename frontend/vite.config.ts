import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Separar las dependencias de React en su propio chunk
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          // Separar Material UI en su propio chunk
          'vendor-mui': ['@mui/material', '@mui/icons-material', '@emotion/react', '@emotion/styled'],
          // Otras bibliotecas utilizadas
          'vendor-utils': ['axios', 'react-dropzone', 'react-markdown']
        }
      }
    },
    // Aumentar el límite de advertencia para chunks grandes
    chunkSizeWarningLimit: 600
  }
})