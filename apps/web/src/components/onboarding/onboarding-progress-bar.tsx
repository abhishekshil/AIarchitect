import type { OnboardingProgress } from '@/types/onboarding';

type Props = {
  progress: OnboardingProgress | null;
  loading?: boolean;
};

export function OnboardingProgressBar({ progress, loading }: Props) {
  if (loading && !progress) {
    return <div className="h-2 w-full animate-pulse rounded-full bg-zinc-200 dark:bg-zinc-700" />;
  }
  if (!progress) return null;

  const pct = Math.min(100, Math.max(0, progress.percent_completed));

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-zinc-600 dark:text-zinc-400">
        <span>
          {progress.by_state?.completed ?? 0} of {progress.total_tasks} tasks completed
        </span>
        <span className="tabular-nums font-medium text-zinc-800 dark:text-zinc-200">{pct}%</span>
      </div>
      <div
        className="h-2 w-full overflow-hidden rounded-full bg-zinc-200 dark:bg-zinc-700"
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="h-full rounded-full bg-emerald-600 transition-[width] duration-300 dark:bg-emerald-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
