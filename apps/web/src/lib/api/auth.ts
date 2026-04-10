import { apiJson } from '@/lib/api/http';
import type { ApiTokenResponse, ApiUser } from '@/types/api';

export async function loginRequest(email: string, password: string): Promise<ApiTokenResponse> {
  return apiJson<ApiTokenResponse>('/api/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function registerRequest(email: string, password: string): Promise<ApiUser> {
  return apiJson<ApiUser>('/api/v1/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function fetchCurrentUser(accessToken: string): Promise<ApiUser> {
  return apiJson<ApiUser>('/api/v1/auth/me', {
    method: 'GET',
    accessToken,
  });
}
