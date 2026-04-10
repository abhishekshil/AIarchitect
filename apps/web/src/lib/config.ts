/**
 * Public env only (embedded in client bundle).
 * Point at your FastAPI origin, e.g. http://127.0.0.1:8000
 */
export function getApiBaseUrl(): string {
  const raw = process.env.NEXT_PUBLIC_API_URL?.trim();
  if (raw) return raw.replace(/\/$/, '');
  return 'http://127.0.0.1:8000';
}
