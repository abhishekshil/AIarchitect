'use client';

import { useAuth } from '@/context/auth-context';
import { clearProjectJourney, getRequirementJourney, journeyStep } from '@/lib/project-journey';
import { deleteRequirement, listRequirements } from '@/lib/api/requirements';
import { createProject, deleteProject, listProjects } from '@/lib/api/projects';
import { ApiRequestError } from '@/lib/api/http';
import type { ApiProject } from '@/types/api';
import type { ApiRequirementSummary } from '@/types/requirement';
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
  const [deletingProjectId, setDeletingProjectId] = useState<string | null>(null);
  const [deletingRequirementId, setDeletingRequirementId] = useState<string | null>(null);
  const [requirementsMap, setRequirementsMap] = useState<Record<string, ApiRequirementSummary[]>>({});

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

  useEffect(() => {
    if (!token || !projects) return;
    let cancelled = false;
    void (async () => {
      const entries = await Promise.all(
        projects.map(async (project) => {
          try {
            const requirements = await listRequirements(token, project.project_id);
            return [project.project_id, requirements] as const;
          } catch {
            return [project.project_id, []] as const;
          }
        }),
      );
      if (cancelled) return;
      setRequirementsMap(Object.fromEntries(entries));
    })();
    return () => {
      cancelled = true;
    };
  }, [token, projects]);

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

  async function onDeleteProject(projectId: string) {
    if (!token) return;
    setDeletingProjectId(projectId);
    setListError(null);
    try {
      await deleteProject(token, projectId);
      clearProjectJourney(projectId);
      setProjects((prev) => (prev ?? []).filter((p) => p.project_id !== projectId));
      setRequirementsMap((prev) => {
        const next = { ...prev };
        delete next[projectId];
        return next;
      });
    } catch (err) {
      setListError(err instanceof ApiRequestError ? err.message : 'Could not delete project');
    } finally {
      setDeletingProjectId(null);
    }
  }

  async function onDeleteRequirement(projectId: string, requirementId: string) {
    if (!token) return;
    setDeletingRequirementId(requirementId);
    setListError(null);
    try {
      await deleteRequirement(token, projectId, requirementId);
      setRequirementsMap((prev) => {
        const current = prev[projectId] ?? [];
        return {
          ...prev,
          [projectId]: current.filter((r) => r.requirement_id !== requirementId),
        };
      });
    } catch (err) {
      setListError(err instanceof ApiRequestError ? err.message : 'Could not delete requirement');
    } finally {
      setDeletingRequirementId(null);
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
              <li key={p.project_id} className="space-y-4 px-4 py-4 first:rounded-t-xl last:rounded-b-xl">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                  <p className="font-medium text-zinc-900 dark:text-zinc-50">{p.name}</p>
                  {p.description ? (
                    <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">{p.description}</p>
                  ) : null}
                  <p className="mt-2 font-mono text-xs text-zinc-400">{p.project_id}</p>
                  </div>
                  <div className="flex shrink-0 flex-col gap-2 sm:flex-row">
                    <button
                      type="button"
                      onClick={() => void onDeleteProject(p.project_id)}
                      disabled={deletingProjectId === p.project_id}
                      className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-center text-sm font-medium text-red-800 hover:bg-red-100 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-200 dark:hover:bg-red-950/60"
                    >
                      {deletingProjectId === p.project_id ? 'Deleting…' : 'Delete project'}
                    </button>
                    <Link
                      href={`/projects/${p.project_id}/requirements/new`}
                      className="rounded-md border border-zinc-200 bg-white px-3 py-2 text-center text-sm font-medium text-emerald-800 hover:bg-zinc-50 dark:border-zinc-600 dark:bg-zinc-900 dark:text-emerald-400 dark:hover:bg-zinc-800"
                    >
                      Add requirement
                    </Link>
                  </div>
                </div>

                <div className="rounded-lg border border-zinc-200 bg-zinc-50/70 p-3 dark:border-zinc-800 dark:bg-zinc-950/40">
                  <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                    Ongoing requirements
                  </p>
                  {(requirementsMap[p.project_id] ?? []).filter((req) => req.project_id === p.project_id).length === 0 ? (
                    <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
                      No requirement yet. Start with Add requirement.
                    </p>
                  ) : (
                    <ul className="mt-2 space-y-2">
                      {(requirementsMap[p.project_id] ?? [])
                        .filter((req) => req.project_id === p.project_id)
                        .map((req) => {
                        const reqJourney = getRequirementJourney(p.project_id, req.requirement_id);
                        const fallbackPath = `/projects/${p.project_id}/requirements/${req.requirement_id}/architecture`;
                        const path = reqJourney?.path ?? fallbackPath;
                        const { step, label } = journeyStep(path);

                        return (
                          <li key={req.requirement_id}>
                            <div className="flex items-center gap-2 rounded-md border border-zinc-200 bg-white px-2 py-2 text-sm dark:border-zinc-700 dark:bg-zinc-900">
                              <Link
                                href={path}
                                className="flex min-w-0 flex-1 items-center justify-between gap-3 rounded-md px-1 py-0.5 hover:bg-zinc-50 dark:hover:bg-zinc-800"
                              >
                                <span className="min-w-0">
                                  <span className="block truncate font-medium text-zinc-800 dark:text-zinc-100">
                                    {req.raw_text_preview || `Requirement v${req.version}`}
                                  </span>
                                  <span className="mt-0.5 block font-mono text-[11px] text-zinc-500">
                                    {req.requirement_id}
                                  </span>
                                </span>
                                <span className="shrink-0 rounded-full bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300">
                                  Step {step}/6 · {label}
                                </span>
                              </Link>
                              <button
                                type="button"
                                onClick={() => void onDeleteRequirement(p.project_id, req.requirement_id)}
                                disabled={deletingRequirementId === req.requirement_id}
                                aria-label="Delete requirement"
                                className="h-7 w-7 shrink-0 rounded-full border border-red-200 text-red-700 hover:bg-red-50 disabled:opacity-50 dark:border-red-900/50 dark:text-red-300 dark:hover:bg-red-950/40"
                              >
                                ×
                              </button>
                            </div>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
