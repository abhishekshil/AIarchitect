'use client';

import { OnboardingFlow } from '@/components/onboarding/onboarding-flow';
import { useAuth } from '@/context/auth-context';
import { useProjectJourneyTracker } from '@/hooks/use-project-journey-tracker';
import { getProject } from '@/lib/api/projects';
import { ApiRequestError } from '@/lib/api/http';
import type { ApiProject } from '@/types/api';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function OnboardingPage() {
  const params = useParams();
  const projectId = typeof params.projectId === 'string' ? params.projectId : '';
  const requirementId = typeof params.requirementId === 'string' ? params.requirementId : '';
  useProjectJourneyTracker(projectId);
  const { token, bootstrapping } = useAuth();
  const [project, setProject] = useState<ApiProject | null>(null);
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId || !token || bootstrapping) return;
    let cancelled = false;
    setLoadState('loading');
    getProject(token, projectId)
      .then((p) => {
        if (!cancelled) {
          setProject(p);
          setLoadState('ready');
          setLoadError(null);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setLoadError(err instanceof ApiRequestError ? err.message : 'Could not load project');
          setLoadState('error');
        }
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, token, bootstrapping]);

  if (!projectId || !requirementId) {
    return (
      <div className="mx-auto max-w-5xl">
        <p className="text-sm text-red-600">Invalid link.</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
            Prepare
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {loadState === 'ready' && project ? project.name : 'Project'}
          </h1>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
            Complete guided setup tasks for your selected architecture. Requirement{' '}
            <span className="font-mono text-xs text-zinc-500">{requirementId}</span>
          </p>
        </div>
      </div>
      {bootstrapping || loadState === 'loading' ? (
        <div className="h-32 animate-pulse rounded-xl bg-zinc-200 dark:bg-zinc-800" />
      ) : null}

      {loadState === 'error' ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
          {loadError}
        </div>
      ) : null}

      {loadState === 'ready' && token ? (
        <OnboardingFlow projectId={projectId} requirementId={requirementId} accessToken={token} />
      ) : null}
    </div>
  );
}
