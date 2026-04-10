import { apiJson } from '@/lib/api/http';
import type { ApiProject } from '@/types/api';

export async function listProjects(accessToken: string): Promise<ApiProject[]> {
  return apiJson<ApiProject[]>('/api/v1/projects', {
    method: 'GET',
    accessToken,
  });
}

export async function getProject(accessToken: string, projectId: string): Promise<ApiProject> {
  return apiJson<ApiProject>(`/api/v1/projects/${projectId}`, {
    method: 'GET',
    accessToken,
  });
}

export async function createProject(
  accessToken: string,
  body: { name: string; description?: string | null },
): Promise<ApiProject> {
  return apiJson<ApiProject>('/api/v1/projects', {
    method: 'POST',
    accessToken,
    body: JSON.stringify(body),
  });
}
