import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  // api-client dipakai sebagai sumber TS dari workspace
  ssr: { noExternal: ['@timesheet/api-client'] },
  server: {
    // Saat dev, /api diteruskan ke FastAPI
    proxy: { '/api': process.env.API_URL ?? 'http://localhost:8000' }
  }
});
