import { formatMatchScore } from '@/components/architecture/estimate-indicators';
import type { ApiArchitectureRecommendationOption } from '@/types/recommendation';

type Props = {
  options: ApiArchitectureRecommendationOption[];
  selectedId: string | null;
  onSelect: (candidateId: string) => void;
};

function tierLabel(estimate: Record<string, unknown> | null): string {
  if (!estimate) return '—';
  const t = estimate.tier;
  return typeof t === 'string' ? t : '—';
}

function numLabel(estimate: Record<string, unknown> | null, key: string): string {
  if (!estimate) return '—';
  const v = estimate[key];
  return typeof v === 'number' ? `${Math.round(v * 100)}%` : '—';
}

export function ArchitectureComparisonTable({ options, selectedId, onSelect }: Props) {
  return (
    <div className="overflow-x-auto rounded-xl border border-zinc-200 dark:border-zinc-800">
      <table className="w-full min-w-[640px] border-collapse text-left text-sm">
        <caption className="sr-only">Architecture options comparison</caption>
        <thead>
          <tr className="border-b border-zinc-200 bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-900/80">
            <th className="px-3 py-2 font-semibold text-zinc-900 dark:text-zinc-50">Select</th>
            <th className="px-3 py-2 font-semibold text-zinc-900 dark:text-zinc-50">Option</th>
            <th className="px-3 py-2 font-semibold text-zinc-900 dark:text-zinc-50">Score</th>
            <th className="px-3 py-2 font-semibold text-zinc-900 dark:text-zinc-50">Cost</th>
            <th className="px-3 py-2 font-semibold text-zinc-900 dark:text-zinc-50">Complexity</th>
            <th className="px-3 py-2 font-semibold text-zinc-900 dark:text-zinc-50">Latency proxy</th>
            <th className="px-3 py-2 font-semibold text-zinc-900 dark:text-zinc-50">Governance</th>
            <th className="px-3 py-2 font-semibold text-zinc-900 dark:text-zinc-50">Trade-offs</th>
          </tr>
        </thead>
        <tbody>
          {options.map((o) => (
            <tr
              key={o.candidate_id}
              className={`border-b border-zinc-100 dark:border-zinc-800/80 ${
                selectedId === o.candidate_id ? 'bg-emerald-50/60 dark:bg-emerald-950/25' : ''
              }`}
            >
              <td className="px-3 py-2 align-top">
                <input
                  type="radio"
                  name="architecture-compare"
                  checked={selectedId === o.candidate_id}
                  onChange={() => onSelect(o.candidate_id)}
                  className="h-4 w-4 border-zinc-300 text-emerald-700"
                />
              </td>
              <td className="px-3 py-2 align-top">
                <p className="font-medium text-zinc-900 dark:text-zinc-50">{o.title}</p>
                <p className="mt-0.5 font-mono text-[10px] text-zinc-400">{o.candidate_id}</p>
              </td>
              <td className="px-3 py-2 align-top tabular-nums text-zinc-700 dark:text-zinc-200">
                {formatMatchScore(o.score)}
              </td>
              <td className="px-3 py-2 align-top capitalize text-zinc-700 dark:text-zinc-200">
                {tierLabel(o.cost_estimate)}
              </td>
              <td className="px-3 py-2 align-top tabular-nums text-zinc-700 dark:text-zinc-200">
                {numLabel(o.complexity_estimate, 'relative')}
              </td>
              <td className="px-3 py-2 align-top tabular-nums text-zinc-700 dark:text-zinc-200">
                {numLabel(o.latency_estimate, 'relative')}
              </td>
              <td className="px-3 py-2 align-top tabular-nums text-zinc-700 dark:text-zinc-200">
                {o.governance_score != null ? `${Math.round(o.governance_score * 100)}%` : '—'}
              </td>
              <td className="max-w-[220px] px-3 py-2 align-top text-xs text-zinc-600 dark:text-zinc-400">
                {o.tradeoffs.slice(0, 2).join(' · ')}
                {o.tradeoffs.length > 2 ? '…' : ''}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
