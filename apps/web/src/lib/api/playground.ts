import { apiJson } from '@/lib/api/http';
import type {
  PlaygroundInferResponse,
  PlaygroundInferenceHistoryEnvelope,
} from '@/types/studio';

export async function playgroundInfer(
  accessToken: string,
  projectId: string,
  body: { runtime_graph_version: number; input_text: string },
): Promise<PlaygroundInferResponse> {
  return apiJson<PlaygroundInferResponse>(`/api/v1/projects/${projectId}/playground/infer`, {
    method: 'POST',
    accessToken,
    body: JSON.stringify(body),
  });
}

export async function listPlaygroundInferenceRuns(
  accessToken: string,
  projectId: string,
  limit = 30,
): Promise<PlaygroundInferenceHistoryEnvelope> {
  const q = new URLSearchParams({ limit: String(limit) });
  return apiJson<PlaygroundInferenceHistoryEnvelope>(
    `/api/v1/projects/${projectId}/playground/inference-runs?${q}`,
    { method: 'GET', accessToken },
  );
}

export async function getPlaygroundInferenceRun(
  accessToken: string,
  projectId: string,
  inferenceId: string,
): Promise<PlaygroundInferResponse> {
  return apiJson<PlaygroundInferResponse>(
    `/api/v1/projects/${projectId}/playground/inference-runs/${inferenceId}`,
    { method: 'GET', accessToken },
  );
}
