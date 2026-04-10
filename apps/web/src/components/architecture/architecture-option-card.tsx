import {
  ComplexityIndicator,
  CostIndicator,
  formatMatchScore,
  GovernanceIndicator,
  LatencyIndicator,
} from '@/components/architecture/estimate-indicators';
import type { ApiArchitectureRecommendationOption } from '@/types/recommendation';

type Props = {
  option: ApiArchitectureRecommendationOption;
  selected: boolean;
  onSelect: () => void;
  name: string;
};

export function ArchitectureOptionCard({ option, selected, onSelect, name }: Props) {
  return (
    <label
      className={`block cursor-pointer rounded-xl border-2 p-5 transition-colors ${
        selected
          ? 'border-emerald-600 bg-emerald-50/50 dark:border-emerald-500 dark:bg-emerald-950/30'
          : 'border-zinc-200 bg-white hover:border-zinc-300 dark:border-zinc-800 dark:bg-zinc-900 dark:hover:border-zinc-600'
      }`}
    >
      <div className="flex gap-3">
        <input
          type="radio"
          name={name}
          checked={selected}
          onChange={onSelect}
          className="mt-1 h-4 w-4 shrink-0 border-zinc-300 text-emerald-700 focus:ring-emerald-600"
        />
        <div className="min-w-0 flex-1 space-y-3">
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-50">{option.title}</h3>
              {option.architecture_template_ref ? (
                <p className="mt-0.5 font-mono text-[11px] text-zinc-400">{option.architecture_template_ref}</p>
              ) : null}
            </div>
            <span className="shrink-0 rounded-full bg-zinc-100 px-2.5 py-1 text-xs font-semibold tabular-nums text-zinc-800 dark:bg-zinc-800 dark:text-zinc-100">
              {formatMatchScore(option.score)}
            </span>
          </div>
          {option.summary ? (
            <p className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-300">{option.summary}</p>
          ) : null}
          {option.rationale ? (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                Why this option
              </p>
              <p className="mt-1 text-sm text-zinc-700 dark:text-zinc-200">{option.rationale}</p>
            </div>
          ) : null}
          <div className="grid gap-4 sm:grid-cols-2">
            <CostIndicator estimate={option.cost_estimate} />
            <GovernanceIndicator score={option.governance_score} />
            <ComplexityIndicator estimate={option.complexity_estimate} />
            <LatencyIndicator estimate={option.latency_estimate} />
          </div>
          {option.tradeoffs.length > 0 ? (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                Trade-offs
              </p>
              <ul className="mt-1 list-inside list-disc text-sm text-zinc-600 dark:text-zinc-300">
                {option.tradeoffs.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            </div>
          ) : null}
          {option.assumptions.length > 0 ? (
            <details className="text-sm text-zinc-600 dark:text-zinc-400">
              <summary className="cursor-pointer font-medium text-zinc-700 dark:text-zinc-300">
                Assumptions ({option.assumptions.length})
              </summary>
              <ul className="mt-2 list-inside list-disc text-xs">
                {option.assumptions.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </details>
          ) : null}
        </div>
      </div>
    </label>
  );
}
