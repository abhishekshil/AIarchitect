'use client';

import type { OnboardingTaskItem, OnboardingValidationFeedback } from '@/types/onboarding';
import { useScreenUiMode } from '@/context/ui-mode-context';
import { useEffect, useState } from 'react';

function FeedbackBlock({ fb }: { fb: OnboardingValidationFeedback }) {
  const errors = fb.errors ?? [];
  const warnings = fb.warnings ?? [];
  if (errors.length === 0 && warnings.length === 0) return null;
  return (
    <div className="space-y-3">
      {errors.length > 0 ? (
        <div
          role="alert"
          className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 dark:border-red-900/50 dark:bg-red-950/40"
        >
          <p className="text-xs font-semibold text-red-900 dark:text-red-200">Fix and resubmit</p>
          <ul className="mt-1 list-inside list-disc text-sm text-red-800 dark:text-red-200">
            {errors.map((e, i) => (
              <li key={i}>{e}</li>
            ))}
          </ul>
        </div>
      ) : null}
      {warnings.length > 0 ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 dark:border-amber-900/40 dark:bg-amber-950/30">
          <p className="text-xs font-semibold text-amber-900 dark:text-amber-200">Suggestions</p>
          <ul className="mt-1 list-inside list-disc text-sm text-amber-900/90 dark:text-amber-100/90">
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}

type Props = {
  task: OnboardingTaskItem;
  unlocked: boolean;
  onStart: () => Promise<void>;
  onSubmit: (body: Record<string, unknown>) => Promise<void>;
  busy: boolean;
};

export function OnboardingTaskPanel({ task, unlocked, onStart, onSubmit, busy }: Props) {
  const { isEffectiveAdvanced: isAdvanced } = useScreenUiMode('prepare');
  const [notes, setNotes] = useState('');
  const [artifactsText, setArtifactsText] = useState('');

  useEffect(() => {
    const n = task.response?.notes;
    setNotes(typeof n === 'string' ? n : '');
    const a = task.response?.artifacts;
    if (Array.isArray(a)) {
      setArtifactsText(
        a.map((x) => (typeof x === 'string' ? x : JSON.stringify(x))).join('\n'),
      );
    } else {
      setArtifactsText('');
    }
  }, [task.node_id, task.response]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const lines = artifactsText
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean);
    const payload: Record<string, unknown> = { notes };
    if (lines.length > 0) payload.artifacts = lines;
    await onSubmit(payload);
  }

  const completed = task.state === 'completed';
  const canEdit = unlocked && !completed;
  const showStart = canEdit && task.state === 'not_started';

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-xl font-semibold text-zinc-900 dark:text-zinc-50">{task.title}</h2>
        {task.description ? (
          <p className="mt-2 text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">{task.description}</p>
        ) : null}
        <div className="mt-3 flex flex-wrap gap-2">
          {isAdvanced && task.condition ? (
            <span className="rounded-full bg-violet-100 px-2 py-0.5 text-xs font-medium text-violet-900 dark:bg-violet-950/60 dark:text-violet-200">
              Condition: {task.condition}
            </span>
          ) : null}
          {isAdvanced
            ? task.guidance_refs.map((ref) => (
                <span
                  key={ref}
                  className="rounded-full bg-zinc-100 px-2 py-0.5 font-mono text-[10px] text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
                >
                  {ref}
                </span>
              ))
            : null}
        </div>
      </header>

      {!unlocked ? (
        <p className="rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2 text-sm text-zinc-600 dark:border-zinc-700 dark:bg-zinc-900/50 dark:text-zinc-400">
          This step unlocks after you complete the previous tasks in the selected order.
        </p>
      ) : null}

      {task.suggestions.length > 0 ? (
        <section>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Guidance
          </h3>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-zinc-700 dark:text-zinc-200">
            {task.suggestions.map((s, i) => (
              <li key={i}>{s}</li>
            ))}
          </ul>
        </section>
      ) : null}

      {task.example_placeholder ? (
        <section>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
            Example
          </h3>
          <p className="mt-1 text-sm italic text-zinc-600 dark:text-zinc-400">{task.example_placeholder}</p>
        </section>
      ) : null}

      {isAdvanced && task.metadata && Object.keys(task.metadata).length > 0 ? (
        <details className="rounded-lg border border-zinc-200 dark:border-zinc-700">
          <summary className="cursor-pointer px-3 py-2 text-xs font-medium text-zinc-700 dark:text-zinc-300">
            Technical metadata
          </summary>
          <pre className="max-h-40 overflow-auto border-t border-zinc-200 p-3 text-[11px] dark:border-zinc-700">
            {JSON.stringify(task.metadata, null, 2)}
          </pre>
        </details>
      ) : null}

      {task.validation_feedback ? <FeedbackBlock fb={task.validation_feedback} /> : null}

      {completed ? (
        <div
          role="status"
          className="rounded-lg border border-emerald-200 bg-emerald-50/90 px-3 py-3 text-sm text-emerald-900 dark:border-emerald-900/50 dark:bg-emerald-950/40 dark:text-emerald-100"
        >
          This step is complete. You can review your notes below (read-only).
        </div>
      ) : null}

      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-4">
        <div>
          <label htmlFor="onb-notes" className="block text-sm font-medium text-zinc-800 dark:text-zinc-200">
            Your notes
          </label>
          <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
            Required. Length rules depend on task type (typically 20+ characters).
          </p>
          <textarea
            id="onb-notes"
            required
            disabled={!canEdit || busy}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={8}
            maxLength={8000}
            className="mt-2 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-600 dark:bg-zinc-950"
          />
        </div>

        <div>
          <label htmlFor="onb-artifacts" className="block text-sm font-medium text-zinc-800 dark:text-zinc-200">
            Artifacts <span className="font-normal text-zinc-500">(optional)</span>
          </label>
          <p className="mt-0.5 text-xs text-zinc-500 dark:text-zinc-400">
            One link or reference per line — prepared for richer file attachments later.
          </p>
          <textarea
            id="onb-artifacts"
            disabled={!canEdit || busy}
            value={artifactsText}
            onChange={(e) => setArtifactsText(e.target.value)}
            rows={3}
            placeholder="https://…&#10;ticket PROJ-123"
            className="mt-2 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-600 dark:bg-zinc-950"
          />
        </div>

        <div className="flex flex-wrap gap-3">
          {showStart ? (
            <button
              type="button"
              disabled={busy}
              onClick={() => void onStart()}
              className="rounded-md border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-50 disabled:opacity-50 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-100 dark:hover:bg-zinc-800"
            >
              {busy ? 'Working…' : 'Mark as started'}
            </button>
          ) : null}
          {canEdit ? (
            <button
              type="submit"
              disabled={busy}
              className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50 dark:bg-emerald-600"
            >
              {busy ? 'Submitting…' : 'Submit step'}
            </button>
          ) : null}
        </div>
      </form>
    </div>
  );
}
