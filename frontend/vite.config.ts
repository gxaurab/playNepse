// import tailwindcss from '@tailwindcss/vite'
// import react from '@vitejs/plugin-react'
// import { defineConfig } from 'vite'

// export default defineConfig({
//   plugins: [react(), tailwindcss()],
//   server: {
//     allowedHosts: ['.trycloudflare.com'],
//     proxy: {
//       '/api': {
//         target: 'http://localhost:8000',
//         changeOrigin: true,
//       },
//       '/ws': {
//         target: 'ws://localhost:8000',
//         ws: true,
//       },
//     },
//   },
//   preview: {
//     allowedHosts: ["alto-busy-humor-impossible.trycloudflare.com"],
//   },
// })

import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const proxy = {
  '/api': { target: 'http://localhost:8000', changeOrigin: true },
  '/ws': { target: 'ws://localhost:8000', ws: true },
}

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: { allowedHosts: true, proxy },
  preview: { allowedHosts: true, proxy },
})