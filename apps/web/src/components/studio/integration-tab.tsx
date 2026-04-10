'use client';

import { CopyButton } from '@/components/studio/copy-button';
import {
  generateCodeSnippets,
  getCodeSnippetBundle,
  listCodeSnippetBundles,
} from '@/lib/api/code-snippets';
import { listRuntimeGraphs } from '@/lib/api/runtime-build';
import { ApiRequestError } from '@/lib/api/http';
import { useScreenUiMode } from '@/context/ui-mode-context';
import type {
  CodeSnippetBundleResponse,
  CodeSnippetBundleSummary,
  SnippetLanguage,
} from '@/types/studio';
import { SNIPPET_LANGUAGES } from '@/types/studio';
import { useCallback, useEffect, useMemo, useState } from 'react';

type Props = {
  projectId: string;
  accessToken: string;
};

const LANG_LABEL: Record<SnippetLanguage, string> = {
  curl: 'cURL',
  javascript: 'JavaScript',
  python: 'Python',
};

export function IntegrationTab({ projectId, accessToken }: Props) {
  const { isEffectiveAdvanced: isAdvanced } = useScreenUiMode('integrate');
  const [bundle, setBundle] = useState<CodeSnippetBundleResponse | null>(null);
  const [bundleList, setBundleList] = useState<CodeSnippetBundleSummary[]>([]);
  const [lang, setLang] = useState<SnippetLanguage>('curl');
  const [versionOverride, setVersionOverride] = useState<string>('');
  const [versions, setVersions] = useState<number[]>([]);
  const [generating, setGenerating] = useState(false);
  const [loadingList, setLoadingList] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const snippetText = useMemo(() => {
    if (!bundle?.snippets) return '';
    return bundle.snippets[lang] ?? bundle.snippets[lang.toLowerCase()] ?? '';
  }, [bundle, lang]);

  const refreshBundles = useCallback(async () => {
    setLoadingList(true);
    try {
      const list = await listCodeSnippetBundles(accessToken, projectId, 15);
      setBundleList(list.bundles);
    } catch {
      setBundleList([]);
    } finally {
      setLoadingList(false);
    }
  }, [accessToken, projectId]);

  useEffect(() => {
    void refreshBundles();
  }, [refreshBundles]);

  useEffect(() => {
    void (async () => {
      try {
        const g = await listRuntimeGraphs(accessToken, projectId);
        setVersions(g.versions.map((x) => x.version).sort((a, b) => b - a));
      } catch {
        setVersions([]);
      }
    })();
  }, [accessToken, projectId]);

  async function onGenerate() {
    setError(null);
    setGenerating(true);
    try {
      const v =
        versionOverride === '' ? null : Number(versionOverride);
      const res = await generateCodeSnippets(
        accessToken,
        projectId,
        v != null && !Number.isNaN(v) && v >= 1 ? v : null,
      );
      setBundle(res);
      void refreshBundles();
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : 'Generate failed');
    } finally {
      setGenerating(false);
    }
  }

  async function onSelectBundle(id: string) {
    setError(null);
    try {
      const res = await getCodeSnippetBundle(accessToken, projectId, id);
      setBundle(res);
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : 'Could not load bundle');
    }
  }

  const availableLangs = useMemo(() => {
    if (!bundle?.snippets) return [...SNIPPET_LANGUAGES];
    return SNIPPET_LANGUAGES.filter((l) => typeof bundle.snippets[l] === 'string');
  }, [bundle]);

  useEffect(() => {
    if (availableLangs.length > 0 && !availableLangs.includes(lang)) {
      setLang(availableLangs[0]);
    }
  }, [availableLangs, lang]);

  return (
    <div className="space-y-8">
      <section className="rounded-xl border border-zinc-200 bg-emerald-50/60 p-5 dark:border-zinc-800 dark:bg-emerald-950/20">
        <h2 className="text-sm font-semibold text-emerald-950 dark:text-emerald-100">Your system is ready to integrate</h2>
        <ol className="mt-3 list-inside list-decimal space-y-2 text-sm text-emerald-950/90 dark:text-emerald-100/90">
          <li>
            Point the web app at your API with <code className="rounded bg-white/80 px-1 dark:bg-zinc-900">NEXT_PUBLIC_API_URL</code> (e.g.{' '}
            <code className="rounded bg-white/80 px-1 dark:bg-zinc-900">http://127.0.0.1:8000</code>).
          </li>
          <li>Sign in via the API (<code className="rounded bg-white/80 px-1 dark:bg-zinc-900">POST /api/v1/auth/login</code>) and use the returned Bearer token.</li>
          <li>
            Replace placeholder tokens in generated code with your JWT. Snippets target this project&apos;s{' '}
            <code className="rounded bg-white/80 px-1 dark:bg-zinc-900">project_id</code> and the chosen runtime graph version.
          </li>
          <li>Use <strong>Run inference</strong> in the Playground tab to validate responses before wiring a client.</li>
        </ol>
      </section>

      <section className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Generate integration bundle</h2>
        <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
          Creates cURL, JavaScript, and Python examples with environment notes and sample request/response for the
          current architecture pattern.
        </p>
        <div className="mt-4 flex flex-wrap items-end gap-4">
          <div>
            <label htmlFor="sn-v" className="block text-xs font-medium text-zinc-600 dark:text-zinc-400">
              Runtime graph version (optional)
            </label>
            <select
              id="sn-v"
              value={versionOverride}
              onChange={(e) => setVersionOverride(e.target.value)}
              className="mt-1 rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm dark:border-zinc-600 dark:bg-zinc-950"
            >
              <option value="">Latest built version</option>
              {versions.map((v) => (
                <option key={v} value={String(v)}>
                  {v}
                </option>
              ))}
            </select>
          </div>
          <button
            type="button"
            disabled={generating}
            onClick={() => void onGenerate()}
            className="rounded-md bg-emerald-700 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50 dark:bg-emerald-600"
          >
            {generating ? 'Generating…' : 'Generate snippets'}
          </button>
        </div>
        {error ? (
          <p className="mt-3 text-sm text-red-600 dark:text-red-400" role="alert">
            {error}
          </p>
        ) : null}
      </section>

      <section className="rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Saved bundles</h2>
        {loadingList ? <p className="mt-2 text-sm text-zinc-500">Loading…</p> : null}
        {bundleList.length > 0 ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {bundleList.map((b) => (
              <button
                key={b.bundle_id}
                type="button"
                onClick={() => void onSelectBundle(b.bundle_id)}
                className="rounded-md border border-zinc-200 px-2 py-1 text-left text-xs hover:bg-zinc-50 dark:border-zinc-700 dark:hover:bg-zinc-800"
              >
                <span className="font-mono">{b.bundle_id.slice(0, 8)}…</span>
                <span className="ml-2 text-zinc-500">v{b.runtime_graph_version}</span>
                <span className="ml-1 text-zinc-400">{b.architecture_pattern}</span>
              </button>
            ))}
          </div>
        ) : (
          !loadingList && <p className="mt-2 text-sm text-zinc-500">None yet — generate above.</p>
        )}
      </section>

      {bundle ? (
        <section className="space-y-4 rounded-xl border border-zinc-200 bg-white p-5 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Snippet bundle</h2>
          <p className="mt-1 text-xs text-zinc-500">
                Pattern <span className="font-medium text-zinc-700 dark:text-zinc-300">{bundle.architecture_pattern}</span> ·
                graph v{bundle.runtime_graph_version}
              </p>
            </div>
            <CopyButton text={snippetText} label={`Copy ${LANG_LABEL[lang]}`} />
          </div>

          <div className="flex flex-wrap gap-2 border-b border-zinc-200 pb-3 dark:border-zinc-700">
            {availableLangs.map((l) => (
              <button
                key={l}
                type="button"
                onClick={() => setLang(l)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium ${
                  lang === l
                    ? 'bg-zinc-900 text-white dark:bg-zinc-100 dark:text-zinc-900'
                    : 'text-zinc-600 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:bg-zinc-800'
                }`}
              >
                {LANG_LABEL[l]}
              </button>
            ))}
          </div>

          {isAdvanced ? (
          <div>
            <h3 className="text-xs font-semibold uppercase text-zinc-500">Environment</h3>
            <div className="mt-2 whitespace-pre-wrap rounded-lg bg-zinc-100 p-3 text-xs text-zinc-800 dark:bg-zinc-950 dark:text-zinc-200">
              {bundle.environment_notes}
            </div>
            <CopyButton text={bundle.environment_notes} label="Copy environment notes" className="mt-2" />
          </div>
          ) : null}

          <div>
            <h3 className="text-xs font-semibold uppercase text-zinc-500">Endpoints</h3>
            <ul className="mt-2 space-y-2 text-sm">
              {bundle.endpoint_metadata.map((e) => (
                <li key={e.name} className="rounded-lg border border-zinc-100 px-3 py-2 dark:border-zinc-800">
                  <span className="font-mono text-xs text-emerald-700 dark:text-emerald-400">{e.method}</span>{' '}
                  <span className="font-mono text-xs">{e.path}</span>
                  {e.description ? (
                    <p className="mt-1 text-xs text-zinc-600 dark:text-zinc-400">{e.description}</p>
                  ) : null}
                </li>
              ))}
            </ul>
          </div>

          {isAdvanced ? (
          <details className="rounded-lg border border-zinc-200 dark:border-zinc-700">
            <summary className="cursor-pointer px-3 py-2 text-sm font-medium text-zinc-700 dark:text-zinc-300">
              Example request / response (JSON)
            </summary>
            <div className="grid gap-4 border-t border-zinc-200 p-3 dark:border-zinc-700 md:grid-cols-2">
              <div>
                <p className="text-xs font-semibold text-zinc-500">Request</p>
                <pre className="mt-1 max-h-40 overflow-auto text-[11px]">
                  {JSON.stringify(bundle.example_request, null, 2)}
                </pre>
              </div>
              <div>
                <p className="text-xs font-semibold text-zinc-500">Response</p>
                <pre className="mt-1 max-h-40 overflow-auto text-[11px]">
                  {JSON.stringify(bundle.example_response, null, 2)}
                </pre>
              </div>
            </div>
          </details>
          ) : null}

          <div>
            <div className="flex items-center justify-between gap-2">
              <h3 className="text-xs font-semibold uppercase text-zinc-500">Code</h3>
              <CopyButton text={snippetText} label="Copy code" />
            </div>
            <pre className="mt-2 max-h-[min(70vh,520px)] overflow-auto rounded-lg bg-zinc-950 p-4 text-xs text-zinc-100">
              {snippetText || 'No snippet for this language.'}
            </pre>
          </div>
          <div className="rounded-lg border border-emerald-200 bg-emerald-50/80 p-3 text-sm text-emerald-900 dark:border-emerald-900/40 dark:bg-emerald-950/30 dark:text-emerald-200">
            Journey complete. Your AI system is ready to ship.
          </div>
        </section>
      ) : null}
    </div>
  );
}
