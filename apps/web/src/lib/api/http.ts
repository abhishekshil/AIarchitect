import { getApiBaseUrl } from '@/lib/config';
import type { ApiErrorBody } from '@/types/api';

export class ApiRequestError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body: unknown) {
    super(message);
    this.name = 'ApiRequestError';
    this.status = status;
    this.body = body;
  }
}

export async function apiJson<T>(
  path: string,
  options: RequestInit & { accessToken?: string | null } = {},
): Promise<T> {
  const { accessToken, headers: initHeaders, ...rest } = options;
  const url = `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
  const headers = new Headers(initHeaders);
  if (!headers.has('Content-Type') && rest.body != null) {
    headers.set('Content-Type', 'application/json');
  }
  if (accessToken) {
    headers.set('Authorization', `Bearer ${accessToken}`);
  }

  const res = await fetch(url, { ...rest, headers });
  const text = await res.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text) as unknown;
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    let detail = res.statusText;
    if (typeof data === 'object' && data !== null && 'detail' in data) {
      const d = (data as ApiErrorBody).detail;
      if (typeof d === 'string') detail = d;
      else if (Array.isArray(d)) detail = d.map((x) => JSON.stringify(x)).join('; ');
    }
    throw new ApiRequestError(detail || `HTTP ${res.status}`, res.status, data);
  }

  return data as T;
}
