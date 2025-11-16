import Constants from 'expo-constants';
import { getHostname } from '../utils/host';

type Extra = { API_BASE_URL?: string };
const extra = (Constants.expoConfig?.extra ?? {}) as Extra;
const isWeb = typeof window !== 'undefined' && typeof document !== 'undefined';

function resolveFromExpo(): string | undefined {
  const value = extra.API_BASE_URL?.trim();
  return value ? value.replace(/\/+$/, '') : undefined;
}

function resolveFromRuntime(): string | undefined {
  const raw = isWeb
    ? (import.meta?.env?.VITE_API_BASE_URL as string | undefined)
    : process.env?.VITE_API_BASE_URL;

  return raw && raw.trim().length > 0 ? raw.trim().replace(/\/+$/, '') : undefined;
}

function resolveFromLan(): string | undefined {
  const host = getHostname();
  return host ? `http://${host}:8000` : undefined;
}

export function resolveApiBaseUrl(): string {
  const fallback =
    typeof __DEV__ !== 'undefined' && __DEV__
      ? 'http://127.0.0.1:8000'
      : 'https://api.konan.tld';

  return (
    resolveFromExpo() ??
    resolveFromRuntime() ??
    resolveFromLan() ??
    fallback
  );
}

export const API_BASE_URL = resolveApiBaseUrl();

export const apiConfig = {
  baseUrl: API_BASE_URL,
  defaultHeaders: {
    'Content-Type': 'application/json',
  },
} as const;

