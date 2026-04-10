'use client';

import { FullscreenArchitectureGraph } from '@/components/architecture/fullscreen-architecture-graph';
import { useAuth } from '@/context/auth-context';
import { ApiRequestError } from '@/lib/api/http';
import { listCandidates } from '@/lib/api/recommendations';
import type { ApiArchitectureRecommendationOption, ScoringMode } from '@/types/recommendation';
import { SCORING_MODES } from '@/types/recommendation';
import Link from 'next/link';
import { useParams, useSearchParams } from 'next/navigation';
import { useEffect, useMemo, useState } from 'react';

function isScoringMode(value: string): value is ScoringMode {
  return (SCORING_MODES as readonly string[]).includes(value);
}

export default function FullscreenGraphPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const projectId = typeof params.projectId === 'string' ? params.projectId : '';
  const requirementId = typeof params.requirementId === 'string' ? params.requirementId : '';
  const candidateId = typeof params.candidateId === 'string' ? params.candidateId : '';
  const sortCandidate = searchParams.get('sort_mode') ?? 'best_overall';
  const sortMode: ScoringMode = isScoringMode(sortCandidate) ? sortCandidate : 'best_overall';
  const { token, bootstrapping } = useAuth();

  const [option, setOption] = useState<ApiArchitectureRecommendationOption | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId || !requirementId || !candidateId || !token || bootstrapping) return;
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const envelope = await listCandidates(token, projectId, requirementId, sortMode);
        if (cancelled) return;
        const candidate = envelope.options.find((item) => item.candidate_id === candidateId) ?? null;
        if (!candidate) {
          setError('Candidate not found. Please return and regenerate options.');
          setOption(null);
          return;
        }
        setOption(candidate);
      } catch (err) {
        if (cancelled) return;
        setError(err instanceof ApiRequestError ? err.message : 'Could not load architecture graph');
        setOption(null);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void load();
    return () => {
      cancelled = true;
    };
  }, [projectId, requirementId, candidateId, token, bootstrapping, sortMode]);

  const backHref = useMemo(
    () => `/projects/${projectId}/requirements/${requirementId}/architecture`,
    [projectId, requirementId],
  );

  if (!projectId || !requirementId || !candidateId) {
    return <p className="text-sm text-red-600">Invalid graph link.</p>;
  }

  return (
    <div className="mx-auto max-w-[1400px] space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-400">
            Full-screen architecture graph
          </p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
            Candidate <span className="font-mono text-sm">{candidateId}</span>
          </h1>
        </div>
        <Link href={backHref} className="text-sm font-medium text-emerald-700 hover:underline dark:text-emerald-400">
          ← Back to architecture options
        </Link>
      </div>

      {loading ? <div className="h-80 animate-pulse rounded-xl bg-zinc-200 dark:bg-zinc-800" aria-busy="true" /> : null}

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-900/40 dark:bg-red-950/40 dark:text-red-200">
          {error}
        </div>
      ) : null}

      {!loading && !error && option ? <FullscreenArchitectureGraph option={option} /> : null}
    </div>
  );
}
