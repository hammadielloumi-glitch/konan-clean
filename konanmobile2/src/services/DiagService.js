import { http } from '../api/http';
export async function pingAPI() {
  // openapi.json ne nécessite pas Auth
  const r = await http.get('/openapi.json', { timeout: 8000 });
  return r.status === 200;
}
