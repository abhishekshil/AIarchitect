'use client';

import { IntegrationTab } from '@/components/studio/integration-tab';
import { PlaygroundTab } from '@/components/studio/playground-tab';
import { RuntimeBuildTab } from '@/components/studio/runtime-build-tab';
import { useAuth } from '@/context/auth-context';
import { useProjectJourneyTracker } from '@/hooks/use-project-journey-tracker';
import { getProject } from '@/lib/api/projects';
import { ApiRequestError } from '@/lib/api/http';
import type { ApiProject } from '@/types/api';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

type StudioSection = 'build' | 'validate' | 'integrate';

type Props = {
  section: StudioSection;
};

export function StudioPageClient({ section }: Props) {
  const params = useParams();
  const projectId = typeof params.projectId === 'string' ? params.projectId : '';
  useProjectJourneyTracker(projectId);
  const { token, bootstrapping } = useAuth();
  const [project, setProject] = useState<ApiProject | null>(null);
  const [loadErr, setLoadErr] = useState<string | null>(null);

  const sectionHeader =
    section === 'build'
      ? {
          eyebrow: 'Build',
          description: 'Compile and prepare your AI system runtime.',
        }
      : section === 'validate'
        ? {
            eyebrow: 'Validate',
            description: 'Test outputs and verify behavior before shipping.',
          }
        : {
            eyebrow: 'Integrate',
            description: 'Generate code snippets and integration-ready assets.',
          };

  useEffect(() => {
    if (!projectId || !token || bootstrapping) return;
    let c = false;
    getProject(token, projectId)
      .then((p) => {
        if (!c) {
          setProject(p);
          setLoadErr(null);
        }
      })
      .catch((e) => {
        if (!c) setLoadErr(e instanceof ApiRequestError ? e.message : 'Failed to load project');
      });
    return () => {
      c = true;
    };
  }, [projectId, token, bootstrapping]);

  if (!projectId) {
    return <p className="text-sm text-red-600">Invalid project.</p>;
  }

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
            {sectionHeader.eyebrow}
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {project?.name ?? 'Project studio'}
          </h1>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
            {sectionHeader.description}
          </p>
        </div>
      </div>
      {loadErr ? (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {loadErr}
        </p>
      ) : null}

      {bootstrapping || !token ? (
        <div className="h-40 animate-pulse rounded-xl bg-zinc-200 dark:bg-zinc-800" />
      ) : (
        <>
          {section === 'build' ? <RuntimeBuildTab projectId={projectId} accessToken={token} /> : null}
          {section === 'validate' ? <PlaygroundTab projectId={projectId} accessToken={token} /> : null}
          {section === 'integrate' ? <IntegrationTab projectId={projectId} accessToken={token} /> : null}
        </>
      )}
    </div>
  );
}
