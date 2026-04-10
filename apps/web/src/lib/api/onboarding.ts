import { apiJson } from '@/lib/api/http';
import type { OnboardingProgress, OnboardingTaskItem, OnboardingTasksEnvelope } from '@/types/onboarding';

export async function listOnboardingTasks(
  accessToken: string,
  projectId: string,
  requirementId: string,
): Promise<OnboardingTasksEnvelope> {
  return apiJson<OnboardingTasksEnvelope>(
    `/api/v1/projects/${projectId}/requirements/${requirementId}/onboarding/tasks`,
    { method: 'GET', accessToken },
  );
}

export async function getOnboardingProgress(
  accessToken: string,
  projectId: string,
  requirementId: string,
): Promise<OnboardingProgress> {
  return apiJson<OnboardingProgress>(
    `/api/v1/projects/${projectId}/requirements/${requirementId}/onboarding/progress`,
    { method: 'GET', accessToken },
  );
}

export async function startOnboardingTask(
  accessToken: string,
  projectId: string,
  requirementId: string,
  nodeId: string,
): Promise<OnboardingTaskItem> {
  const enc = encodeURIComponent(nodeId);
  return apiJson<OnboardingTaskItem>(
    `/api/v1/projects/${projectId}/requirements/${requirementId}/onboarding/tasks/${enc}/start`,
    { method: 'POST', accessToken },
  );
}

export async function submitOnboardingTask(
  accessToken: string,
  projectId: string,
  requirementId: string,
  nodeId: string,
  response: Record<string, unknown>,
): Promise<OnboardingTaskItem> {
  const enc = encodeURIComponent(nodeId);
  return apiJson<OnboardingTaskItem>(
    `/api/v1/projects/${projectId}/requirements/${requirementId}/onboarding/tasks/${enc}/submit`,
    {
      method: 'POST',
      accessToken,
      body: JSON.stringify({ response }),
    },
  );
}
