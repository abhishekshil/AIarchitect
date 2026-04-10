'use client';

import { listRequirements } from '@/lib/api/requirements';
import { getRuntimeBuildJob, listRuntimeGraphs, startRuntimeBuild } from '@/lib/api/runtime-build';
import { ApiRequestError } from '@/lib/api/http';
import type { ApiRequirementSummary } from '@/types/requirement';
import type { RuntimeBuildJobResponse, RuntimeGraphListEnvelope } from '@/types/studio';
import { useCallback, useEffect, useState } from 'react';

type Props = {
  projectId: string;
  accessToken: string;
};

function isTerminalJob(status: string): boolean {
  return status === 'succeeded' || status === 'failed';
}

export function RuntimeBuildTab({ projectId, accessToken }: Props) {
  const [requirements, setRequirements] = useState<ApiRequirementSummary[] | null>(null);
  const [reqError, setReqError] = useState<string | null>(null);
  const [selectedReq, setSelectedReq] = useState('');
  const [graphs, setGraphs] = useState<RuntimeGraphListEnvelope | null>(null);
  const [job, setJob] = useState<RuntimeBuildJobResponse | null>(null);
  const [starting, setStarting] = useState(false);
  const [graphsLoading, setGraphsLoading] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const refreshGraphs = useCallback(async () => {
    setGraphsLoading(true);
    try {
      const g = await listRuntimeGraphs(accessToken, projectId);
      setGraphs(g);
    } catch {
      setGraphs(null);
    } finally {
      setGraphsLoading(false);
    }
  }, [accessToken, projectId]);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const rows = await listRequirements(accessToken, projectId);
        if (!cancelled) {
          setRequirements(rows);
          setReqError(null);
          setSelectedReq((prev) => prev || rows[0]?.requirement_id || '');
        }
      } catch (err) {
        if (!cancelled) {
          setReqError(err instanceof ApiRequestError ? err.message : 'Could not load requirements');
          setRequirements([]);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [accessToken, projectId]);

  useEffect(() => {
    void refreshGraphs();
  }, [refreshGraphs]);

  useEffect(() => {
    if (!job || isTerminalJob(job.status)) return;
    const t = setInterval(() => {
      void (async () => {
        try {
          const j = await getRuntimeBuildJob(accessToken, projectId, job.job_id);
          setJob(j);
          if (isTerminalJob(j.status)) void refreshGraphs();
        } catch {
          /* keep last job state */
        }
      })();
    }, 1500);
    return () => clearInterval(t);
  }, [job, accessToken, projectId, refreshGraphs]);

  async function onStartBuild() {
    if (!selectedReq) return;
    setActionError(null);
    setStarting(true);
    try {
      const j = await startRuntimeBuild(accessToken, projectId, selectedReq);
      setJob(j);
    } catch (err) {
      setActionError(err instanceof ApiRequestError ? err.message : 'Failed to start build');
    } finally {
      setStarting(false);
    }
  }

  return (
    <div className="space-y-8">
      <section className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Compile runtime graph</h2>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          Queues a build from your architecture selection and onboarding progress for the chosen requirement.
        </p>
        {reqError ? (
          <p className="mt-3 text-sm text-red-600 dark:text-red-400">{reqError}</p>
        ) : null}
        <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-end">
          <div className="min-w-0 flex-1">
            <label htmlFor="studio-req" className="block text-xs font-medium text-zinc-600 dark:text-zinc-400">
              Requirement
            </label>
            <select
              id="studio-req"
              value={selectedReq}
              onChange={(e) => setSelectedReq(e.target.value)}
              className="mt-1 w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-600 dark:bg-zinc-950"
            >
              {(requirements ?? []).length === 0 ? (
                <option value="">No requirements — create one first</option>
              ) : null}
              {(requirements ?? []).map((r) => (
                <option key={r.requirement_id} value={r.requirement_id}>
                  v{r.version} · {r.raw_text_preview.slice(0, 60)}
                  {r.raw_text_preview.length > 60 ? '…' : ''}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            disabled={!selectedReq || starting}
            onClick={() => void onStartBuild()}
            className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50 dark:bg-emerald-600"
          >
            {starting ? 'Starting…' : 'Start build'}
          </button>
        </div>
        {actionError ? (
          <p className="mt-3 text-sm text-red-600 dark:text-red-400">{actionError}</p>
        ) : null}
      </section>

      {job ? (
        <section
          className={`rounded-xl border p-5 ${
            job.status === 'failed'
              ? 'border-red-200 bg-red-50 dark:border-red-900/40 dark:bg-red-950/30'
              : job.status === 'succeeded'
                ? 'border-emerald-200 bg-emerald-50/80 dark:border-emerald-900/40 dark:bg-emerald-950/25'
                : 'border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900'
          }`}
        >
          <h3 className="text-sm font-semibold uppercase tracking-wide text-zinc-600 dark:text-zinc-400">
            Build job
          </h3>
          <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-xs text-zinc-500">Job ID</dt>
              <dd className="font-mono text-xs break-all">{job.job_id}</dd>
            </div>
            <div>
              <dt className="text-xs text-zinc-500">Status</dt>
              <dd className="font-medium capitalize">{job.status}</dd>
            </div>
            <div>
              <dt className="text-xs text-zinc-500">Stage</dt>
              <dd>{job.stage}</dd>
            </div>
            {job.runtime_graph_version != null ? (
              <div>
                <dt className="text-xs text-zinc-500">Runtime graph version</dt>
                <dd className="font-semibold">{job.runtime_graph_version}</dd>
              </div>
            ) : null}
          </dl>
          {job.error_detail ? (
            <p className="mt-3 text-sm text-red-800 dark:text-red-200">{job.error_detail}</p>
          ) : null}
        </section>
      ) : null}

      <section className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Runtime graph versions</h2>
          <button
            type="button"
            disabled={graphsLoading}
            onClick={() => void refreshGraphs()}
            className="text-sm font-medium text-emerald-700 hover:underline disabled:opacity-50 dark:text-emerald-400"
          >
            Refresh
          </button>
        </div>
        {graphsLoading && !graphs ? (
          <p className="mt-4 text-sm text-zinc-500">Loading…</p>
        ) : null}
        {graphs && graphs.versions.length === 0 ? (
          <p className="mt-4 text-sm text-zinc-600 dark:text-zinc-400">
            No compiled graphs yet. Run a build after architecture selection and onboarding.
          </p>
        ) : null}
        {graphs && graphs.versions.length > 0 ? (
          <ul className="mt-4 divide-y divide-zinc-200 dark:divide-zinc-800">
            {graphs.versions.map((v) => (
              <li key={v.runtime_graph_id} className="flex flex-wrap items-center justify-between gap-2 py-3 text-sm">
                <span className="font-medium text-zinc-900 dark:text-zinc-50">Version {v.version}</span>
                <span className="font-mono text-xs text-zinc-500">{v.runtime_graph_id}</span>
                <span className="text-xs text-zinc-500">{new Date(v.created_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        ) : null}
      </section>
    </div>
  );
}
