import type { Handle } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

// Produksi (adapter-node): teruskan /api ke FastAPI. Saat `npm run dev`, proxy Vite yang menangani.
export const handle: Handle = async ({ event, resolve }) => {
  if (event.url.pathname.startsWith('/api')) {
    const target = (env.API_URL ?? 'http://localhost:8000') + event.url.pathname + event.url.search;
    const headers = new Headers(event.request.headers);
    headers.delete('host');
    const hasBody = !['GET', 'HEAD'].includes(event.request.method);
    return fetch(target, {
      method: event.request.method,
      headers,
      body: hasBody ? event.request.body : undefined,
      // @ts-expect-error duplex dibutuhkan Node untuk body streaming
      duplex: 'half'
    });
  }
  return resolve(event);
};
