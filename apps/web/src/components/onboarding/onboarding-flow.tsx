'use client';

import {
  getOnboardingProgress,
  listOnboardingTasks,
  startOnboardingTask,
  submitOnboardingTask,
} from '@/lib/api/onboarding';
import { ApiRequestError } from '@/lib/api/http';
import { topologicalOrder } from '@/lib/onboarding/graph-order';
import { isTaskUnlocked } from '@/lib/onboarding/task-unlock';
import { OnboardingProgressBar } from '@/components/onboarding/onboarding-progress-bar';
import { OnboardingTaskPanel } from '@/components/onboarding/onboarding-task-panel';
import { OnboardingTaskSidebar } from '@/components/onboarding/onboarding-task-sidebar';
import { useScreenUiMode } from '@/context/ui-mode-context';
import type { FlowOrderMode, OnboardingProgress, OnboardingTaskItem, OnboardingTasksEnvelope } from '@/types/onboarding';
import Link from 'next/link';
import { useCallback, useEffect, useMemo, useState } from 'react';

type Props = {
  projectId: string;
  requirementId: string;
  accessToken: string;
};

function mergeTask(tasks: OnboardingTaskItem[], updated: OnboardingTaskItem): OnboardingTaskItem[] {
  return tasks.map((t) => (t.node_id === updated.node_id ? updated : t));
}

export function OnboardingFlow({ projectId, requirementId, accessToken }: Props) {
  const { isEffectiveAdvanced: isAdvanced } = useScreenUiMode('prepare');
  const [envelope, setEnvelope] = useState<OnboardingTasksEnvelope | null>(null);
  const [progress, setProgress] = useState<OnboardingProgress | null>(null);
  const [orderMode, setOrderMode] = useState<FlowOrderMode>('linear');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    setLoadError(null);
    try {
      const [env, prog] = await Promise.all([
        listOnboardingTasks(accessToken, projectId, requirementId),
        getOnboardingProgress(accessToken, projectId, requirementId),
      ]);
      setEnvelope(env);
      setProgress(prog);
    } catch (err) {
      setLoadError(err instanceof ApiRequestError ? err.message : 'Failed to load onboarding');
      setEnvelope(null);
      setProgress(null);
    }
  }, [accessToken, projectId, requirementId]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    void (async () => {
      try {
        const [env, prog] = await Promise.all([
          listOnboardingTasks(accessToken, projectId, requirementId),
          getOnboardingProgress(accessToken, projectId, requirementId),
        ]);
        if (!cancelled) {
          setEnvelope(env);
          setProgress(prog);
          setLoadError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setLoadError(err instanceof ApiRequestError ? err.message : 'Failed to load onboarding');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [accessToken, projectId, requirementId]);

  const byId = useMemo(() => {
    const m = new Map<string, OnboardingTaskItem>();
    for (const t of envelope?.tasks ?? []) m.set(t.node_id, t);
    return m;
  }, [envelope]);

  const orderedIds = useMemo(() => {
    const tasks = envelope?.tasks ?? [];
    const ids = tasks.map((t) => t.node_id);
    const edges = envelope?.edges ?? [];
    if (orderMode === 'graph' && edges.length > 0) {
      return topologicalOrder(ids, edges, ids);
    }
    return ids;
  }, [envelope, orderMode]);

  const orderedTasks = useMemo(() => {
    return orderedIds.map((id) => byId.get(id)).filter((t): t is OnboardingTaskItem => Boolean(t));
  }, [orderedIds, byId]);

  useEffect(() => {
    if (!envelope || orderedTasks.length === 0) return;
    if (selectedId && byId.has(selectedId)) return;
    const firstOpen = orderedTasks.find(
      (t) =>
        isTaskUnlocked(t, byId, envelope.edges, orderedIds, orderMode) && t.state !== 'completed',
    );
    setSelectedId((firstOpen ?? orderedTasks[0]).node_id);
  }, [envelope, orderedTasks, byId, selectedId, orderMode, orderedIds]);

  const selectedTask = selectedId ? byId.get(selectedId) : undefined;
  const selectedUnlocked = selectedTask
    ? isTaskUnlocked(selectedTask, byId, envelope?.edges ?? [], orderedIds, orderMode)
    : false;

  async function handleStart() {
    if (!selectedTask) return;
    setBusy(true);
    try {
      const updated = await startOnboardingTask(
        accessToken,
        projectId,
        requirementId,
        selectedTask.node_id,
      );
      setEnvelope((prev) =>
        prev ? { ...prev, tasks: mergeTask(prev.tasks, updated) } : prev,
      );
      setLoadError(null);
      await refresh();
    } catch (err) {
      setLoadError(err instanceof ApiRequestError ? err.message : 'Could not start task');
    } finally {
      setBusy(false);
    }
  }

  async function handleSubmit(body: Record<string, unknown>) {
    if (!selectedTask) return;
    setBusy(true);
    try {
      const updated = await submitOnboardingTask(
        accessToken,
        projectId,
        requirementId,
        selectedTask.node_id,
        body,
      );
      setEnvelope((prev) =>
        prev ? { ...prev, tasks: mergeTask(prev.tasks, updated) } : prev,
      );
      setLoadError(null);
      await refresh();
    } catch (err) {
      setLoadError(err instanceof ApiRequestError ? err.message : 'Submit failed');
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-4" aria-busy="true">
        <div className="h-8 w-64 animate-pulse rounded bg-zinc-200 dark:bg-zinc-700" />
        <div className="h-40 animate-pulse rounded-xl bg-zinc-200 dark:bg-zinc-700" />
      </div>
    );
  }

  if (loadError && !envelope) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-6 dark:border-red-900/40 dark:bg-red-950/40">
        <p className="text-sm font-medium text-red-900 dark:text-red-100">{loadError}</p>
        <p className="mt-2 text-sm text-red-800 dark:text-red-200">
          Select an architecture for this requirement first, then return here.
        </p>
      </div>
    );
  }

  if (!envelope || orderedTasks.length === 0) {
    return (
      <p className="text-sm text-zinc-600 dark:text-zinc-400">
        No onboarding tasks are available yet for this requirement.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      {loadError ? (
        <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/40 dark:text-amber-100">
          {loadError}
        </p>
      ) : null}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <OnboardingProgressBar progress={progress} />
        {isAdvanced ? (
          <div className="flex shrink-0 gap-2">
            <button
              type="button"
              onClick={() => setOrderMode('linear')}
              className={`rounded-md px-3 py-1.5 text-xs font-medium ${
                orderMode === 'linear'
                  ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                  : 'border border-zinc-300 text-zinc-700 dark:border-zinc-600 dark:text-zinc-300'
              }`}
            >
              Linear order
            </button>
            <button
              type="button"
              onClick={() => setOrderMode('graph')}
              className={`rounded-md px-3 py-1.5 text-xs font-medium ${
                orderMode === 'graph'
                  ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                  : 'border border-zinc-300 text-zinc-700 dark:border-zinc-600 dark:text-zinc-300'
              }`}
            >
              Dependency order
            </button>
          </div>
        ) : null}
      </div>
      {isAdvanced ? (
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          <strong>Linear</strong> follows the default list. <strong>Dependency order</strong> uses graph edges
          when present; steps stay locked until predecessors are completed.
        </p>
      ) : (
        <p className="text-xs text-zinc-500 dark:text-zinc-400">
          Follow steps in order and complete each one to unlock the next.
        </p>
      )}

      <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
        <aside className="w-full shrink-0 lg:w-72">
          <OnboardingTaskSidebar
            orderedTasks={orderedTasks}
            selectedId={selectedId}
            onSelect={setSelectedId}
            byId={byId}
            edges={envelope.edges}
            orderMode={orderMode}
            orderedIds={orderedIds}
          />
        </aside>
        <div className="min-w-0 flex-1 rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
          {selectedTask ? (
            <OnboardingTaskPanel
              task={selectedTask}
              unlocked={selectedUnlocked}
              onStart={handleStart}
              onSubmit={handleSubmit}
              busy={busy}
            />
          ) : (
            <p className="text-sm text-zinc-500">Select a step.</p>
          )}
        </div>
      </div>
      {progress && progress.percent_completed >= 100 ? (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/80 p-4 dark:border-emerald-900/40 dark:bg-emerald-950/30">
          <p className="text-sm text-emerald-900 dark:text-emerald-200">
            Prepare completed. Continue to build your runtime.
          </p>
          <Link
            href={`/projects/${projectId}/studio/build`}
            className="mt-3 inline-flex rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 dark:bg-emerald-600"
          >
            Next: Build
          </Link>
        </div>
      ) : null}
    </div>
  );
}
