'use client';

import { useAuth } from '@/context/auth-context';
import { listProjects } from '@/lib/api/projects';
import { ApiRequestError } from '@/lib/api/http';
import Link from 'next/link';
import { useEffect, useState } from 'react';

export default function DashboardPage() {
  const { token } = useAuth();
  const [projectCount, setProjectCount] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    listProjects(token)
      .then((rows) => {
        if (!cancelled) setProjectCount(rows.length);
      })
      .catch((err) => {
        if (!cancelled)
          setError(err instanceof ApiRequestError ? err.message : 'Could not load projects');
      });
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Welcome back
        </h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          Continue your AI architecture journey from idea to integration.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <section className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
          <h2 className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Projects</h2>
          <p className="mt-2 text-3xl font-semibold tabular-nums text-zinc-900 dark:text-zinc-50">
            {projectCount === null && !error ? '—' : error ? '!' : projectCount}
          </p>
          {error ? <p className="mt-2 text-xs text-red-600 dark:text-red-400">{error}</p> : null}
          <div className="mt-4 flex flex-col gap-2 text-sm">
            <Link
              href="/projects"
              className="font-medium text-emerald-700 hover:underline dark:text-emerald-400"
            >
              Manage projects →
            </Link>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Open a project and use <span className="font-medium">Add requirement</span> to capture
              intent.
            </p>
          </div>
        </section>
        <section className="rounded-xl border border-dashed border-zinc-300 bg-zinc-50/80 p-5 dark:border-zinc-700 dark:bg-zinc-900/50">
          <h2 className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Workflows</h2>
          <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
            Workflow screens are available now via each project.
          </p>
          <div className="mt-4 flex flex-col gap-2 text-sm">
            <Link
              href="/projects"
              className="font-medium text-emerald-700 hover:underline dark:text-emerald-400"
            >
              Open projects →
            </Link>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">
              Then follow: <span className="font-medium">Requirements</span> →{' '}
              <span className="font-medium">Architecture</span> →{' '}
              <span className="font-medium">Onboarding</span> →{' '}
              <span className="font-medium">Build &amp; Runtime</span>.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
