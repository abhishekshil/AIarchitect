'use client';

import { useAuth } from '@/context/auth-context';
import { createProject, listProjects } from '@/lib/api/projects';
import { ApiRequestError } from '@/lib/api/http';
import type { ApiProject } from '@/types/api';
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';

export default function ProjectsPage() {
  const { token } = useAuth();
  const [projects, setProjects] = useState<ApiProject[] | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [createError, setCreateError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    if (!token) return;
    setListError(null);
    try {
      const rows = await listProjects(token);
      setProjects(rows);
    } catch (err) {
      setListError(err instanceof ApiRequestError ? err.message : 'Failed to load projects');
      setProjects([]);
    }
  }, [token]);

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    setCreateError(null);
    setCreating(true);
    try {
      const created = await createProject(token, {
        name: name.trim(),
        description: description.trim() || null,
      });
      setName('');
      setDescription('');
      setProjects((prev) => (prev ? [created, ...prev] : [created]));
    } catch (err) {
      setCreateError(err instanceof ApiRequestError ? err.message : 'Create failed');
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Projects
          </h1>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Create a workspace for each solution you are planning.
          </p>
        </div>
        <Link
          href="/dashboard"
          className="text-sm font-medium text-emerald-700 hover:underline dark:text-emerald-400"
        >
          ← Dashboard
        </Link>
      </div>

      <section className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">New project</h2>
        <form onSubmit={onCreate} className="mt-4 space-y-3">
          <div>
            <label htmlFor="pname" className="block text-xs font-medium text-zinc-600 dark:text-zinc-400">
              Name
            </label>
            <input
              id="pname"
              required
              maxLength={200}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Customer support copilot"
              className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-600 dark:bg-zinc-950"
            />
          </div>
          <div>
            <label htmlFor="pdesc" className="block text-xs font-medium text-zinc-600 dark:text-zinc-400">
              Description <span className="font-normal text-zinc-400">(optional)</span>
            </label>
            <textarea
              id="pdesc"
              rows={2}
              maxLength={4000}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Short context for your team"
              className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-600 dark:bg-zinc-950"
            />
          </div>
          {createError ? (
            <p className="text-sm text-red-600 dark:text-red-400" role="alert">
              {createError}
            </p>
          ) : null}
          <button
            type="submit"
            disabled={creating}
            className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50 dark:bg-emerald-600 dark:hover:bg-emerald-500"
          >
            {creating ? 'Creating…' : 'Create project'}
          </button>
        </form>
      </section>

      <section>
        <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Your projects</h2>
        {listError ? (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400">{listError}</p>
        ) : null}
        {projects === null ? (
          <p className="mt-4 text-sm text-zinc-500">Loading…</p>
        ) : projects.length === 0 ? (
          <p className="mt-4 rounded-lg border border-dashed border-zinc-300 bg-zinc-50 px-4 py-8 text-center text-sm text-zinc-500 dark:border-zinc-700 dark:bg-zinc-900/50 dark:text-zinc-400">
            No projects yet. Create one above.
          </p>
        ) : (
          <ul className="mt-4 divide-y divide-zinc-200 rounded-xl border border-zinc-200 bg-white dark:divide-zinc-800 dark:border-zinc-800 dark:bg-zinc-900">
            {projects.map((p) => (
              <li
                key={p.project_id}
                className="flex flex-col gap-3 px-4 py-4 first:rounded-t-xl last:rounded-b-xl sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0">
                  <p className="font-medium text-zinc-900 dark:text-zinc-50">{p.name}</p>
                  {p.description ? (
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{p.description}</p>
                  ) : null}
                  <p className="mt-2 font-mono text-xs text-zinc-400">{p.project_id}</p>
                </div>
                <div className="flex shrink-0 flex-col gap-2 sm:flex-row">
                  <Link
                    href={`/projects/${p.project_id}/studio`}
                    className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-center text-sm font-medium text-emerald-900 hover:bg-emerald-100 dark:border-emerald-900/50 dark:bg-emerald-950/40 dark:text-emerald-200 dark:hover:bg-emerald-950/60"
                  >
                    Studio
                  </Link>
                  <Link
                    href={`/projects/${p.project_id}/requirements/new`}
                    className="rounded-md border border-zinc-200 bg-white px-3 py-2 text-center text-sm font-medium text-emerald-800 hover:bg-zinc-50 dark:border-zinc-600 dark:bg-zinc-900 dark:text-emerald-400 dark:hover:bg-zinc-800"
                  >
                    Add requirement
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
