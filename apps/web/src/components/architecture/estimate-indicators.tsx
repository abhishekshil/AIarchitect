import type { JsonObject } from '@/types/recommendation';

function tierStyles(tier: string): string {
  const t = tier.toLowerCase();
  if (t === 'low')
    return 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-200';
  if (t === 'medium')
    return 'bg-amber-100 text-amber-950 dark:bg-amber-950/50 dark:text-amber-100';
  if (t === 'high')
    return 'bg-red-100 text-red-900 dark:bg-red-950/60 dark:text-red-200';
  return 'bg-zinc-100 text-zinc-800 dark:bg-zinc-800 dark:text-zinc-200';
}

export function CostIndicator({ estimate }: { estimate: JsonObject | null }) {
  if (!estimate) return <span className="text-xs text-zinc-400">—</span>;
  const tier = typeof estimate.tier === 'string' ? estimate.tier : '—';
  const notes = typeof estimate.notes === 'string' ? estimate.notes : null;
  return (
    <div className="flex flex-col gap-1">
      <span
        className={`inline-flex w-fit rounded-full px-2 py-0.5 text-xs font-medium capitalize ${tierStyles(tier)}`}
      >
        Cost: {tier}
      </span>
      {notes ? <span className="text-[11px] leading-snug text-zinc-500 dark:text-zinc-400">{notes}</span> : null}
    </div>
  );
}

export function ComplexityIndicator({ estimate }: { estimate: JsonObject | null }) {
  if (!estimate) return <span className="text-xs text-zinc-400">—</span>;
  const rel = typeof estimate.relative === 'number' ? estimate.relative : null;
  const notes = typeof estimate.notes === 'string' ? estimate.notes : null;
  const pct = rel != null ? Math.round(rel * 100) : null;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between gap-2 text-xs">
        <span className="font-medium text-zinc-700 dark:text-zinc-300">Complexity</span>
        {pct != null ? <span className="tabular-nums text-zinc-500">{pct}%</span> : null}
      </div>
      {pct != null ? (
        <div
          className="h-1.5 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-700"
          title={notes ?? undefined}
        >
          <div
            className="h-full rounded-full bg-violet-600 dark:bg-violet-500"
            style={{ width: `${pct}%` }}
          />
        </div>
      ) : null}
      {notes ? <p className="text-[11px] leading-snug text-zinc-500 dark:text-zinc-400">{notes}</p> : null}
    </div>
  );
}

export function LatencyIndicator({ estimate }: { estimate: JsonObject | null }) {
  if (!estimate) return <span className="text-xs text-zinc-400">—</span>;
  const rel = typeof estimate.relative === 'number' ? estimate.relative : null;
  const notes = typeof estimate.notes === 'string' ? estimate.notes : null;
  const pct = rel != null ? Math.round(rel * 100) : null;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between gap-2 text-xs">
        <span className="font-medium text-zinc-700 dark:text-zinc-300">Time to value</span>
        {pct != null ? <span className="tabular-nums text-zinc-500">{pct}%</span> : null}
      </div>
      {pct != null ? (
        <div
          className="h-1.5 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-700"
          title={notes ?? undefined}
        >
          <div
            className="h-full rounded-full bg-sky-600 dark:bg-sky-500"
            style={{ width: `${pct}%` }}
          />
        </div>
      ) : null}
      <p className="text-[11px] leading-snug text-zinc-500 dark:text-zinc-400">
        {notes ?? 'Higher score means lower latency risk in this mock model.'}
      </p>
    </div>
  );
}

export function GovernanceIndicator({ score }: { score: number | null }) {
  if (score == null) return <span className="text-xs text-zinc-400">—</span>;
  const pct = Math.round(score * 100);
  return (
    <div className="text-xs">
      <span className="font-medium text-zinc-700 dark:text-zinc-300">Governance fit</span>
      <div className="mt-1 flex items-center gap-2">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-700">
          <div
            className="h-full rounded-full bg-teal-600 dark:bg-teal-500"
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="tabular-nums text-zinc-500">{pct}%</span>
      </div>
    </div>
  );
}

export function formatMatchScore(score: number | null): string {
  if (score == null) return '—';
  return `${Math.round(score * 100)}% match`;
}
