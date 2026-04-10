import { apiJson } from '@/lib/api/http';
import type { RuntimeBuildJobResponse, RuntimeGraphListEnvelope } from '@/types/studio';

export async function startRuntimeBuild(
  accessToken: string,
  projectId: string,
  requirementId: string,
): Promise<RuntimeBuildJobResponse> {
  return apiJson<RuntimeBuildJobResponse>(
    `/api/v1/projects/${projectId}/requirements/${requirementId}/runtime-build`,
    { method: 'POST', accessToken },
  );
}

export async function getRuntimeBuildJob(
  accessToken: string,
  projectId: string,
  jobId: string,
): Promise<RuntimeBuildJobResponse> {
  return apiJson<RuntimeBuildJobResponse>(
    `/api/v1/projects/${projectId}/runtime-builds/${jobId}`,
    { method: 'GET', accessToken },
  );
}

export async function listRuntimeGraphs(
  accessToken: string,
  projectId: string,
): Promise<RuntimeGraphListEnvelope> {
  return apiJson<RuntimeGraphListEnvelope>(`/api/v1/projects/${projectId}/runtime-graphs`, {
    method: 'GET',
    accessToken,
  });
}
