import { apiJson } from '@/lib/api/http';
import type { ApiRequirementSubmitResponse, ApiRequirementSummary } from '@/types/requirement';

export async function listRequirements(
  accessToken: string,
  projectId: string,
): Promise<ApiRequirementSummary[]> {
  return apiJson<ApiRequirementSummary[]>(`/api/v1/projects/${projectId}/requirements`, {
    method: 'GET',
    accessToken,
  });
}

export async function submitRequirement(
  accessToken: string,
  projectId: string,
  rawText: string,
): Promise<ApiRequirementSubmitResponse> {
  return apiJson<ApiRequirementSubmitResponse>(
    `/api/v1/projects/${projectId}/requirements`,
    {
      method: 'POST',
      accessToken,
      body: JSON.stringify({ raw_text: rawText }),
    },
  );
}

export async function deleteRequirement(
  accessToken: string,
  projectId: string,
  requirementId: string,
): Promise<void> {
  await apiJson<void>(`/api/v1/projects/${projectId}/requirements/${requirementId}`, {
    method: 'DELETE',
    accessToken,
  });
}
