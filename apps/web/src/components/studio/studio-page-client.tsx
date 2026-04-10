'use client';

import { IntegrationTab } from '@/components/studio/integration-tab';
import { PlaygroundTab } from '@/components/studio/playground-tab';
import { RuntimeBuildTab } from '@/components/studio/runtime-build-tab';
import { useAuth } from '@/context/auth-context';
import { getProject } from '@/lib/api/projects';
import { ApiRequestError } from '@/lib/api/http';
import type { ApiProject } from '@/types/api';
import type { StudioTabId } from '@/types/studio';
import Link from 'next/link';
import { useParams, useSearchParams } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';

function tabFromQuery(raw: string | null): StudioTabId {
  if (raw === 'playground' || raw === 'integration') return raw;
  return 'build';
}

const TABS: { id: StudioTabId; label: string }[] = [
  { id: 'build', label: 'Build & runtime' },
  { id: 'playground', label: 'Playground' },
  { id: 'integration', label: 'Integration' },
];

export function StudioPageClient() {
  const params = useParams();
  const searchParams = useSearchParams();
  const projectId = typeof params.projectId === 'string' ? params.projectId : '';
  const { token, bootstrapping } = useAuth();
  const [project, setProject] = useState<ApiProject | null>(null);
  const [loadErr, setLoadErr] = useState<string | null>(null);
  const tab = useMemo(
    () => tabFromQuery(searchParams.get('tab')),
    [searchParams],
  );

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

  const tabHref = useMemo(() => {
    return (id: StudioTabId) =>
      `/projects/${projectId}/studio${id === 'build' ? '' : `?tab=${id}`}`;
  }, [projectId]);

  if (!projectId) {
    return <p className="text-sm text-red-600">Invalid project.</p>;
  }

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
            Build · test · integrate
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {project?.name ?? 'Project studio'}
          </h1>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
            Compile runtime graphs, run mock inference, and export client snippets.
          </p>
        </div>
        <Link href="/projects" className="text-sm font-medium text-emerald-700 hover:underline dark:text-emerald-400">
          ← Projects
        </Link>
      </div>

      {loadErr ? (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {loadErr}
        </p>
      ) : null}

      <div className="flex flex-wrap gap-2 border-b border-zinc-200 dark:border-zinc-800">
        {TABS.map(({ id, label }) => (
          <Link
            key={id}
            href={tabHref(id)}
            scroll={false}
            className={`border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
              tab === id
                ? 'border-emerald-600 text-emerald-800 dark:border-emerald-500 dark:text-emerald-300'
                : 'border-transparent text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100'
            }`}
          >
            {label}
          </Link>
        ))}
      </div>

      {bootstrapping || !token ? (
        <div className="h-40 animate-pulse rounded-xl bg-zinc-200 dark:bg-zinc-800" />
      ) : (
        <>
          {tab === 'build' ? <RuntimeBuildTab projectId={projectId} accessToken={token} /> : null}
          {tab === 'playground' ? <PlaygroundTab projectId={projectId} accessToken={token} /> : null}
          {tab === 'integration' ? <IntegrationTab projectId={projectId} accessToken={token} /> : null}
        </>
      )}
    </div>
  );
}
