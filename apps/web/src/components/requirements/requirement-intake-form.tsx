'use client';

import { AttachmentsPlaceholder } from '@/components/requirements/attachments-placeholder';
import { useScreenUiMode } from '@/context/ui-mode-context';
import { submitRequirement } from '@/lib/api/requirements';
import { ApiRequestError } from '@/lib/api/http';
import type { ApiRequirementSubmitResponse } from '@/types/requirement';
import Link from 'next/link';
import { useCallback, useState } from 'react';

const MAX_LEN = 50_000;

type Props = {
  projectId: string;
  projectName: string;
  accessToken: string;
};

type SubmitState = 'idle' | 'loading' | 'error' | 'success';

export function RequirementIntakeForm({ projectId, projectName, accessToken }: Props) {
  const { isEffectiveAdvanced: isAdvanced } = useScreenUiMode('define');
  const [rawText, setRawText] = useState('');
  const [state, setState] = useState<SubmitState>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<ApiRequirementSubmitResponse | null>(null);

  const reset = useCallback(() => {
    setRawText('');
    setState('idle');
    setErrorMessage(null);
    setResult(null);
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = rawText.trim();
    if (!trimmed) {
      setErrorMessage('Enter a description of what you need.');
      setState('error');
      return;
    }
    setState('loading');
    setErrorMessage(null);
    setResult(null);
    try {
      const res = await submitRequirement(accessToken, projectId, trimmed);
      setResult(res);
      setState('success');
    } catch (err) {
      setErrorMessage(err instanceof ApiRequestError ? err.message : 'Submission failed');
      setState('error');
    }
  }

  if (state === 'success' && result) {
    const { revision, normalization } = result;
    const p = revision.profile;
    return (
      <div className="space-y-6">
        <div
          role="status"
          className="rounded-xl border border-emerald-200 bg-emerald-50/90 p-5 dark:border-emerald-900/60 dark:bg-emerald-950/40"
        >
          <p className="text-sm font-semibold text-emerald-900 dark:text-emerald-100">
            Requirement saved
          </p>
          <p className="mt-1 text-sm text-emerald-800/90 dark:text-emerald-200/90">
            Version {revision.version} recorded for <span className="font-medium">{projectName}</span>.
          </p>
          <dl className="mt-4 grid gap-2 text-xs text-emerald-900/80 dark:text-emerald-200/80 sm:grid-cols-2">
            <div>
              <dt className="font-medium text-emerald-800 dark:text-emerald-300">Requirement ID</dt>
              <dd className="mt-0.5 font-mono break-all">{revision.requirement_id}</dd>
            </div>
            {p.primary_task_type ? (
              <div>
                <dt className="font-medium text-emerald-800 dark:text-emerald-300">Primary task</dt>
                <dd className="mt-0.5">{p.primary_task_type}</dd>
              </div>
            ) : null}
            <div className="sm:col-span-2">
              <dt className="font-medium text-emerald-800 dark:text-emerald-300">Normalization</dt>
              <dd className="mt-0.5">{normalization.method}</dd>
            </div>
          </dl>
          {normalization.rationale.length > 0 ? (
            <ul className="mt-3 list-inside list-disc text-xs text-emerald-900/85 dark:text-emerald-200/85">
              {normalization.rationale.map((line, i) => (
                <li key={i}>{line}</li>
              ))}
            </ul>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-3">
          <Link
            href={`/projects/${projectId}/requirements/${revision.requirement_id}/architecture`}
            className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            Next: Decide
          </Link>
          <button
            type="button"
            onClick={reset}
            className="rounded-md border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-800 hover:bg-zinc-50 dark:border-zinc-600 dark:text-zinc-100 dark:hover:bg-zinc-800"
          >
            Submit another
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <form onSubmit={onSubmit} className="space-y-6">
        <div className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Describe what you want to build</h2>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            Keep it in plain language. We will infer structure and suggest the best architecture next.
          </p>
          <div className="flex items-baseline justify-between gap-2">
            <label htmlFor="raw-text" className="mt-4 text-sm font-semibold text-zinc-900 dark:text-zinc-50">
              Requirement
            </label>
            <span className="text-xs tabular-nums text-zinc-500 dark:text-zinc-400">
              {rawText.length} / {MAX_LEN}
            </span>
          </div>
          <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
            Describe goals, users, data sources, constraints, and success criteria in free form.
          </p>
          <textarea
            id="raw-text"
            name="raw_text"
            required
            minLength={1}
            maxLength={MAX_LEN}
            rows={14}
            value={rawText}
            onChange={(e) => setRawText(e.target.value)}
            disabled={state === 'loading'}
            placeholder="Example: We need an internal Q&A assistant over our Confluence and Slack history, with citations and access control for engineering employees."
            className="mt-3 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm leading-relaxed text-zinc-900 placeholder:text-zinc-400 disabled:opacity-60 dark:border-zinc-600 dark:bg-zinc-950 dark:text-zinc-50 dark:placeholder:text-zinc-500"
          />
        </div>

        <AttachmentsPlaceholder />
        {isAdvanced ? (
          <details className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
            <summary className="cursor-pointer text-sm font-semibold text-zinc-800 dark:text-zinc-100">
              Advanced constraints
            </summary>
            <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">
              Constraint editing is currently inferred automatically by the backend normalizer. In a future version,
              this section will support direct latency/cost/compliance controls.
            </p>
          </details>
        ) : null}

        {state === 'error' && errorMessage ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800 dark:border-red-900/50 dark:bg-red-950/50 dark:text-red-200">
            {errorMessage}
          </p>
        ) : null}

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="submit"
            disabled={state === 'loading' || rawText.trim().length === 0}
            className="rounded-md bg-emerald-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50 dark:bg-emerald-600 dark:hover:bg-emerald-500"
          >
            {state === 'loading' ? 'Analyzing…' : 'Analyze requirement'}
          </button>
          {state === 'loading' ? (
            <span className="text-sm text-zinc-500 dark:text-zinc-400">Understanding your requirement and preparing architecture options…</span>
          ) : null}
        </div>
      </form>
    </div>
  );
}
