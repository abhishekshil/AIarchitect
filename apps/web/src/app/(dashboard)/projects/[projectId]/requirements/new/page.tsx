'use client';

import { RequirementIntakeForm } from '@/components/requirements/requirement-intake-form';
import { useAuth } from '@/context/auth-context';
import { getProject } from '@/lib/api/projects';
import { ApiRequestError } from '@/lib/api/http';
import type { ApiProject } from '@/types/api';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function NewRequirementPage() {
  const params = useParams();
  const projectId = typeof params.projectId === 'string' ? params.projectId : '';
  const { token, bootstrapping } = useAuth();
  const [project, setProject] = useState<ApiProject | null>(null);
  const [loadState, setLoadState] = useState<'loading' | 'error' | 'ready'>('loading');
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId || !token || bootstrapping) return;
    let cancelled = false;
    setLoadState('loading');
    setLoadError(null);
    getProject(token, projectId)
      .then((p) => {
        if (!cancelled) {
          setProject(p);
          setLoadState('ready');
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setLoadError(err instanceof ApiRequestError ? err.message : 'Could not load project');
          setLoadState('error');
          setProject(null);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [projectId, token, bootstrapping]);

  if (!projectId) {
    return (
      <div className="mx-auto max-w-3xl">
        <p className="text-sm text-red-600 dark:text-red-400">Invalid project link.</p>
        <Link href="/projects" className="mt-4 inline-block text-sm text-emerald-700 dark:text-emerald-400">
          ← Projects
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
            Requirement intake
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            {loadState === 'ready' && project ? project.name : 'Project'}
          </h1>
          {loadState === 'ready' && project?.description ? (
            <p className="mt-2 max-w-xl text-sm text-zinc-600 dark:text-zinc-400">{project.description}</p>
          ) : null}
        </div>
        <Link
          href="/projects"
          className="shrink-0 text-sm font-medium text-emerald-700 hover:underline dark:text-emerald-400"
        >
          ← All projects
        </Link>
      </div>

      {bootstrapping || loadState === 'loading' ? (
        <div
          className="rounded-xl border border-zinc-200 bg-white p-8 dark:border-zinc-800 dark:bg-zinc-900"
          role="status"
          aria-busy="true"
          aria-label="Loading project"
        >
          <div className="h-4 w-48 animate-pulse rounded bg-zinc-200 dark:bg-zinc-700" />
          <div className="mt-4 h-32 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-800" />
        </div>
      ) : null}

      {loadState === 'error' ? (
        <div
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 p-5 dark:border-red-900/50 dark:bg-red-950/40"
        >
          <p className="text-sm font-medium text-red-900 dark:text-red-100">Could not load project</p>
          <p className="mt-1 text-sm text-red-800 dark:text-red-200">{loadError}</p>
          <Link
            href="/projects"
            className="mt-4 inline-block text-sm font-medium text-red-800 underline dark:text-red-300"
          >
            Back to projects
          </Link>
        </div>
      ) : null}

      {loadState === 'ready' && project && token ? (
        <RequirementIntakeForm projectId={projectId} projectName={project.name} accessToken={token} />
      ) : null}
    </div>
  );
}
