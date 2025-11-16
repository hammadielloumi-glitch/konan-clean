import { apiConfig } from '../config/config';

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

async function http<T>(path: string, init: RequestInit = {}): Promise<T> {
  const { baseUrl, defaultHeaders } = apiConfig;
  const url = `${baseUrl}${path}`;
  const headers = {
    ...defaultHeaders,
    ...(init.headers ?? {}),
  };

  const response = await fetch(url, {
    credentials: init.credentials ?? 'include',
    ...init,
    headers,
  });

  const contentType = response.headers.get('content-type') ?? '';
  const isJson = contentType.includes('application/json');
  const body = isJson ? await response.json() : await response.text();

  if (!response.ok) {
    const detail = isJson ? JSON.stringify(body) : body || '';
    throw new Error(`HTTP ${response.status} ${response.statusText}: ${detail}`);
  }

  return body as T;
}

export const client = {
  get: <T>(path: string, init?: RequestInit) =>
    http<T>(path, { ...(init ?? {}), method: 'GET' }),
  post: <T>(path: string, body?: unknown, init?: RequestInit) =>
    http<T>(path, {
      ...(init ?? {}),
      method: 'POST',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  put: <T>(path: string, body?: unknown, init?: RequestInit) =>
    http<T>(path, {
      ...(init ?? {}),
      method: 'PUT',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body?: unknown, init?: RequestInit) =>
    http<T>(path, {
      ...(init ?? {}),
      method: 'PATCH',
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string, init?: RequestInit) =>
    http<T>(path, { ...(init ?? {}), method: 'DELETE' }),
};

export { http };