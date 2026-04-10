'use client';

import { CopyButton } from '@/components/studio/copy-button';
import {
  getPlaygroundInferenceRun,
  listPlaygroundInferenceRuns,
  playgroundInfer,
} from '@/lib/api/playground';
import { listRuntimeGraphs } from '@/lib/api/runtime-build';
import { ApiRequestError } from '@/lib/api/http';
import { useScreenUiMode } from '@/context/ui-mode-context';
import type { PlaygroundInferenceRunSummary, PlaygroundInferResponse } from '@/types/studio';
import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';

type Props = {
  projectId: string;
  accessToken: string;
};

export function PlaygroundTab({ projectId, accessToken }: Props) {
  const { isEffectiveAdvanced: isAdvanced } = useScreenUiMode('validate');
  const [versions, setVersions] = useState<number[]>([]);
  const [version, setVersion] = useState(1);
  const [inputText, setInputText] = useState('');
  const [result, setResult] = useState<PlaygroundInferResponse | null>(null);
  const [runSummaries, setRunSummaries] = useState<PlaygroundInferenceRunSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [runsLoading, setRunsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshVersions = useCallback(async () => {
    try {
      const g = await listRuntimeGraphs(accessToken, projectId);
      const vs = g.versions.map((x) => x.version).sort((a, b) => b - a);
      setVersions(vs);
      if (vs.length > 0) setVersion((v) => (vs.includes(v) ? v : vs[0]));
    } catch {
      setVersions([]);
    }
  }, [accessToken, projectId]);

  const refreshRuns = useCallback(async () => {
    setRunsLoading(true);
    try {
      const h = await listPlaygroundInferenceRuns(accessToken, projectId, 25);
      setRunSummaries(h.runs);
    } catch {
      setRunSummaries([]);
    } finally {
      setRunsLoading(false);
    }
  }, [accessToken, projectId]);

  useEffect(() => {
    void refreshVersions();
  }, [refreshVersions]);

  useEffect(() => {
    void refreshRuns();
  }, [refreshRuns]);

  async function onRun() {
    const t = inputText.trim();
    if (!t) {
      setError('Enter prompt text.');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const res = await playgroundInfer(accessToken, projectId, {
        runtime_graph_version: version,
        input_text: t,
      });
      setResult(res);
      void refreshRuns();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : 'Inference failed');
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  async function loadRun(id: string) {
    setError(null);
    try {
      const res = await getPlaygroundInferenceRun(accessToken, projectId, id);
      setResult(res);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : 'Could not load run');
    }
  }

  const active = result;

  return (
    <div className="space-y-8">
      <section className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Mock inference</h2>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          {isAdvanced
            ? 'Runs the architecture-aware mock engine. Output shape (citations, traces, structured fields) depends on the compiled graph pattern (RAG, hybrid, etc.).'
            : 'Test how your AI system responds before integrating it into your app.'}
        </p>
        <div className="mt-4 flex flex-wrap items-end gap-4">
          <div>
            <label htmlFor="pg-version" className="block text-xs font-medium text-zinc-600">
              Runtime graph version
            </label>
            <select
              id="pg-version"
              value={version}
              onChange={(e) => setVersion(Number(e.target.value))}
              className="mt-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-600 dark:bg-zinc-950"
            >
              {versions.length === 0 ? <option value={1}>1 (build a graph first)</option> : null}
              {versions.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-4">
          <label htmlFor="pg-input" className="block text-xs font-medium text-zinc-600 dark:text-zinc-400">
            Input
          </label>
          <textarea
            id="pg-input"
            rows={5}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={loading}
            placeholder="Ask a question or describe a scenario to test…"
            className="mt-1 w-full rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-600 dark:bg-zinc-950"
          />
        </div>
        {error ? (
          <p className="mt-2 text-sm text-red-600 dark:text-red-400" role="alert">
            {error}
          </p>
        ) : null}
        <button
          type="button"
          disabled={loading || versions.length === 0}
          onClick={() => void onRun()}
          className="mt-4 rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50 dark:bg-emerald-600"
        >
          {loading ? 'Running…' : 'Run inference'}
        </button>
      </section>

      {active ? (
        <section className="space-y-6 rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h3 className="text-sm font-semibold uppercase tracking-wide text-zinc-500">Result</h3>
              <p className="mt-1 text-xs text-zinc-500">
                Pattern: <span className="font-medium text-zinc-800 dark:text-zinc-200">{active.architecture_pattern}</span>{' '}
                · Graph v{active.runtime_graph_version}
              </p>
            </div>
            <CopyButton text={JSON.stringify(active, null, 2)} label="Copy JSON" />
          </div>
          <div>
            <h4 className="text-xs font-semibold text-zinc-500">Output</h4>
            <p className="mt-2 whitespace-pre-wrap text-sm text-zinc-800 dark:text-zinc-200">{active.output_text}</p>
          </div>
          {active.structured_output && Object.keys(active.structured_output).length > 0 ? (
            <div>
              <h4 className="text-xs font-semibold text-zinc-500">Structured output</h4>
              <pre className="mt-2 max-h-48 overflow-auto rounded-lg bg-zinc-100 p-3 text-xs dark:bg-zinc-950">
                {JSON.stringify(active.structured_output, null, 2)}
              </pre>
            </div>
          ) : null}
          {active.citations.length > 0 ? (
            <div>
              <h4 className="text-xs font-semibold text-zinc-500">Citations</h4>
              <ul className="mt-2 space-y-2">
                {active.citations.map((c) => (
                  <li
                    key={c.citation_id}
                    className="rounded-lg border border-zinc-200 p-3 text-sm dark:border-zinc-700"
                  >
                    <p className="font-mono text-xs text-emerald-700 dark:text-emerald-400">{c.source_ref}</p>
                    <p className="mt-1 text-zinc-700 dark:text-zinc-200">{c.snippet}</p>
                    <p className="mt-1 text-xs text-zinc-500">score: {c.score.toFixed(3)}</p>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {isAdvanced && active.traces.length > 0 ? (
            <div>
              <h4 className="text-xs font-semibold text-zinc-500">Trace</h4>
              <div className="mt-2 overflow-x-auto">
                <table className="w-full min-w-[480px] border-collapse text-left text-xs">
                  <thead>
                    <tr className="border-b border-zinc-200 dark:border-zinc-700">
                      <th className="py-2 pr-2">#</th>
                      <th className="py-2 pr-2">Node</th>
                      <th className="py-2 pr-2">Type</th>
                      <th className="py-2 pr-2">Action</th>
                      <th className="py-2">Detail</th>
                    </tr>
                  </thead>
                  <tbody>
                    {active.traces.map((t) => (
                      <tr key={t.step_index} className="border-b border-zinc-100 dark:border-zinc-800">
                        <td className="py-2 pr-2 tabular-nums text-zinc-500">{t.step_index}</td>
                        <td className="py-2 pr-2 font-mono text-zinc-700 dark:text-zinc-300">{t.node_id ?? '—'}</td>
                        <td className="py-2 pr-2">{t.component_type ?? '—'}</td>
                        <td className="py-2 pr-2">{t.action}</td>
                        <td className="py-2 font-mono text-[10px] text-zinc-500">
                          {JSON.stringify(t.detail)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : null}
          {isAdvanced ? (
            <div>
              <h4 className="text-xs font-semibold text-zinc-500">Metadata</h4>
              <pre className="mt-2 max-h-40 overflow-auto rounded-lg bg-zinc-100 p-3 text-xs dark:bg-zinc-950">
                {JSON.stringify(active.metadata, null, 2)}
              </pre>
            </div>
          ) : null}
        </section>
      ) : null}
      {active ? (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/80 p-4 dark:border-emerald-900/40 dark:bg-emerald-950/30">
          <p className="text-sm text-emerald-900 dark:text-emerald-200">
            Validation run completed. Continue to integration.
          </p>
          <Link
            href={`/projects/${projectId}/studio/integrate`}
            className="mt-3 inline-flex rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 dark:bg-emerald-600"
          >
            Next: Integrate
          </Link>
        </div>
      ) : null}

      <section className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Recent runs</h2>
          <button
            type="button"
            disabled={runsLoading}
            onClick={() => void refreshRuns()}
            className="text-sm text-emerald-700 hover:underline disabled:opacity-50 dark:text-emerald-400"
          >
            Refresh
          </button>
        </div>
        {runsLoading && runSummaries.length === 0 ? (
          <p className="mt-4 text-sm text-zinc-500">Loading…</p>
        ) : null}
        {runSummaries.length === 0 && !runsLoading ? (
          <p className="mt-4 text-sm text-zinc-500">No saved runs yet.</p>
        ) : null}
        <ul className="mt-4 space-y-2">
          {runSummaries.map((r) => (
            <li key={r.inference_id}>
              <button
                type="button"
                onClick={() => void loadRun(r.inference_id)}
                className="w-full rounded-lg border border-zinc-200 px-3 py-2 text-left text-sm hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-800/80"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-[10px] text-zinc-500">{r.inference_id}</span>
                  <span className="text-xs text-zinc-400">v{r.runtime_graph_version}</span>
                  <span className="rounded bg-zinc-100 px-1.5 py-0.5 text-[10px] dark:bg-zinc-800">
                    {r.architecture_pattern}
                  </span>
                </div>
                <p className="mt-1 line-clamp-2 text-xs text-zinc-600 dark:text-zinc-400">{r.input_preview}</p>
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
