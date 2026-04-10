import { apiJson } from '@/lib/api/http';
import type {
  ApiArchitectureRecommendationsEnvelope,
  ApiArchitectureSelectionEnvelope,
  ScoringMode,
} from '@/types/recommendation';

function scoringQuery(mode: ScoringMode): string {
  const p = new URLSearchParams({ sort_mode: mode });
  return `?${p.toString()}`;
}

export async function listCandidates(
  accessToken: string,
  projectId: string,
  requirementId: string,
  sortMode: ScoringMode = 'best_overall',
): Promise<ApiArchitectureRecommendationsEnvelope> {
  const q = scoringQuery(sortMode);
  return apiJson<ApiArchitectureRecommendationsEnvelope>(
    `/api/v1/projects/${projectId}/requirements/${requirementId}/candidates${q}`,
    { method: 'GET', accessToken },
  );
}

export async function generateCandidates(
  accessToken: string,
  projectId: string,
  requirementId: string,
  sortMode: ScoringMode = 'best_overall',
): Promise<ApiArchitectureRecommendationsEnvelope> {
  const q = scoringQuery(sortMode);
  return apiJson<ApiArchitectureRecommendationsEnvelope>(
    `/api/v1/projects/${projectId}/requirements/${requirementId}/candidates/generate${q}`,
    { method: 'POST', accessToken },
  );
}

export async function selectArchitecture(
  accessToken: string,
  projectId: string,
  requirementId: string,
  candidateId: string,
): Promise<ApiArchitectureSelectionEnvelope> {
  return apiJson<ApiArchitectureSelectionEnvelope>(
    `/api/v1/projects/${projectId}/requirements/${requirementId}/architecture-selection`,
    {
      method: 'POST',
      accessToken,
      body: JSON.stringify({ candidate_id: candidateId }),
    },
  );
}
