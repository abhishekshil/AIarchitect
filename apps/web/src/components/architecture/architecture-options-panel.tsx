'use client';

import { ArchitectureComparisonTable } from '@/components/architecture/architecture-comparison-table';
import { ArchitectureOptionCard } from '@/components/architecture/architecture-option-card';
import { generateCandidates, listCandidates, selectArchitecture } from '@/lib/api/recommendations';
import { ApiRequestError } from '@/lib/api/http';
import type { ApiArchitectureRecommendationsEnvelope, ApiArchitectureSelectionEnvelope, ScoringMode } from '@/types/recommendation';
import { SCORING_MODES } from '@/types/recommendation';
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';

type ViewMode = 'cards' | 'table';

type Props = {
  projectId: string;
  projectName: string;
  requirementId: string;
  accessToken: string;
};

export function ArchitectureOptionsPanel({
  projectId,
  projectName,
  requirementId,
  accessToken,
}: Props) {
  const [sortMode, setSortMode] = useState<ScoringMode>('best_overall');
  const [envelope, setEnvelope] = useState<ApiArchitectureRecommendationsEnvelope | null>(null);
  const [listLoading, setListLoading] = useState(true);
  const [generateLoading, setGenerateLoading] = useState(false);
  const [listError, setListError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectLoading, setSelectLoading] = useState(false);
  const [selectError, setSelectError] = useState<string | null>(null);
  const [success, setSuccess] = useState<ApiArchitectureSelectionEnvelope | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('cards');

  const loadList = useCallback(async () => {
    setListError(null);
    setListLoading(true);
    try {
      const data = await listCandidates(accessToken, projectId, requirementId, sortMode);
      setEnvelope(data);
      setSelectedId(null);
    } catch (err) {
      setListError(err instanceof ApiRequestError ? err.message : 'Could not load options');
      setEnvelope(null);
    } finally {
      setListLoading(false);
    }
  }, [accessToken, projectId, requirementId, sortMode]);

  useEffect(() => {
    void loadList();
  }, [loadList]);

  async function onGenerate() {
    setListError(null);
    setGenerateLoading(true);
    try {
      const data = await generateCandidates(accessToken, projectId, requirementId, sortMode);
      setEnvelope(data);
      setSelectedId(null);
    } catch (err) {
      setListError(err instanceof ApiRequestError ? err.message : 'Could not generate options');
    } finally {
      setGenerateLoading(false);
    }
  }

  async function onConfirmSelection() {
    if (!selectedId) return;
    setSelectError(null);
    setSelectLoading(true);
    try {
      const res = await selectArchitecture(accessToken, projectId, requirementId, selectedId);
      setSuccess(res);
    } catch (err) {
      setSelectError(err instanceof ApiRequestError ? err.message : 'Selection failed');
    } finally {
      setSelectLoading(false);
    }
  }

  const options = envelope?.options ?? [];
  const radioName = `architecture-${requirementId}`;

  if (success) {
    const nTasks = success.task_graph.nodes?.length ?? 0;
    return (
      <div className="space-y-6">
        <div
          role="status"
          className="rounded-xl border border-emerald-200 bg-emerald-50/90 p-6 dark:border-emerald-900/50 dark:bg-emerald-950/40"
        >
          <h2 className="text-lg font-semibold text-emerald-900 dark:text-emerald-100">
            Architecture selected
          </h2>
          <p className="mt-2 text-sm text-emerald-800 dark:text-emerald-200">
            Your choice is saved for <span className="font-medium">{projectName}</span>. We generated{' '}
            <span className="font-medium">{nTasks}</span> onboarding tasks to configure this design.
          </p>
          <dl className="mt-4 grid gap-2 text-xs text-emerald-900/90 dark:text-emerald-200/90 sm:grid-cols-2">
            <div>
              <dt className="font-medium">Selection ID</dt>
              <dd className="mt-0.5 font-mono break-all">{success.selection.selection_id}</dd>
            </div>
            <div>
              <dt className="font-medium">Candidate</dt>
              <dd className="mt-0.5 font-mono break-all">{success.selection.solution_candidate_id}</dd>
            </div>
          </dl>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/projects/${projectId}/requirements/${requirementId}/onboarding`}
            className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 dark:bg-emerald-600"
          >
            Continue to onboarding
          </Link>
          <Link
            href="/dashboard"
            className="rounded-md border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-100 dark:hover:bg-zinc-800"
          >
            Dashboard
          </Link>
          <Link
            href={`/projects/${projectId}/requirements/new`}
            className="rounded-md border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-100 dark:hover:bg-zinc-800"
          >
            New requirement
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:flex-wrap sm:items-end sm:justify-between">
        <div className="space-y-2">
          <label htmlFor="sort-mode" className="block text-xs font-medium text-zinc-600 dark:text-zinc-400">
            Ranking emphasis
          </label>
          <select
            id="sort-mode"
            value={sortMode}
            onChange={(e) => setSortMode(e.target.value as ScoringMode)}
            className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-600 dark:bg-zinc-950"
          >
            {SCORING_MODES.map((m) => (
              <option key={m} value={m}>
                {m.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
          <p className="max-w-md text-xs text-zinc-500 dark:text-zinc-400">
            Regenerating applies this emphasis. For a first pass, use &quot;best overall&quot; — then switch
            to cost- or speed-focused views to compare.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setViewMode('cards')}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              viewMode === 'cards'
                ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                : 'border border-zinc-300 text-zinc-700 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-300 dark:hover:bg-zinc-800'
            }`}
          >
            Overview cards
          </button>
          <button
            type="button"
            onClick={() => setViewMode('table')}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              viewMode === 'table'
                ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                : 'border border-zinc-300 text-zinc-700 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-300 dark:hover:bg-zinc-800'
            }`}
          >
            Comparison table
          </button>
        </div>
      </div>

      {listError ? (
        <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
          {listError}
        </p>
      ) : null}

      {listLoading ? (
        <div className="space-y-4" aria-busy="true" aria-label="Loading architecture options">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-40 animate-pulse rounded-xl bg-zinc-200 dark:bg-zinc-800" />
          ))}
        </div>
      ) : null}

      {!listLoading && options.length === 0 ? (
        <div className="rounded-xl border border-dashed border-zinc-300 bg-zinc-50/80 p-8 text-center dark:border-zinc-600 dark:bg-zinc-900/40">
          <p className="text-sm text-zinc-600 dark:text-zinc-300">
            No architecture options yet for this requirement. Generate a ranked set from your requirement
            profile.
          </p>
          <button
            type="button"
            disabled={generateLoading}
            onClick={() => void onGenerate()}
            className="mt-4 rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50 dark:bg-emerald-600"
          >
            {generateLoading ? 'Generating…' : 'Generate options'}
          </button>
        </div>
      ) : null}

      {!listLoading && options.length > 0 ? (
        <>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-zinc-600 dark:text-zinc-400">
              {options.length} option{options.length === 1 ? '' : 's'} — pick one, then confirm below.
            </p>
            <button
              type="button"
              disabled={generateLoading}
              onClick={() => void onGenerate()}
              className="text-sm font-medium text-emerald-700 hover:underline disabled:opacity-50 dark:text-emerald-400"
            >
              {generateLoading ? 'Regenerating…' : 'Regenerate with current ranking'}
            </button>
          </div>

          {viewMode === 'cards' ? (
            <div className="space-y-4">
              {options.map((opt) => (
                <ArchitectureOptionCard
                  key={opt.candidate_id}
                  option={opt}
                  selected={selectedId === opt.candidate_id}
                  onSelect={() => setSelectedId(opt.candidate_id)}
                  name={radioName}
                />
              ))}
            </div>
          ) : (
            <ArchitectureComparisonTable
              options={options}
              selectedId={selectedId}
              onSelect={setSelectedId}
            />
          )}

          {selectError ? (
            <p className="text-sm text-red-600 dark:text-red-400" role="alert">
              {selectError}
            </p>
          ) : null}

          <div className="flex flex-wrap items-center gap-3 border-t border-zinc-200 pt-6 dark:border-zinc-800">
            <button
              type="button"
              disabled={!selectedId || selectLoading}
              onClick={() => void onConfirmSelection()}
              className="rounded-md bg-emerald-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50 dark:bg-emerald-600"
            >
              {selectLoading ? 'Saving…' : 'Confirm architecture choice'}
            </button>
            {!selectedId ? (
              <span className="text-xs text-zinc-500">Select an option in the cards or table first.</span>
            ) : null}
          </div>
        </>
      ) : null}
    </div>
  );
}
