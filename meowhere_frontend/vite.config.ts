import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Adres backendu dla proxy. Sprawdzamy OBIE nazwy zmiennych, żeby nie było
// cichego fallbacku, gdy compose ustawia jedną, a config czyta drugą:
//   - VITE_API_TARGET     <- ustawiane w docker-compose.yml
//   - VITE_BACKEND_PROXY  <- starsza nazwa
// Fallback (localhost:8000) działa tylko dla Vite odpalonego na hoście.
const backendTarget =
  process.env.VITE_API_TARGET ||
  process.env.VITE_BACKEND_PROXY ||
  'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',   // widoczny poza kontenerem
    port: 5173,
    strictPort: true,
    proxy: {
      // Wszystko idzie przez ten sam origin => zero problemów z CORS.
      '/api': {
        target: backendTarget,
        changeOrigin: true,
      },
      // Statyczne pliki wgranych zdjęć.
      '/uploads': {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
})
