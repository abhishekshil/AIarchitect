import { isTaskUnlocked } from '@/lib/onboarding/task-unlock';
import { useScreenUiMode } from '@/context/ui-mode-context';
import type { FlowOrderMode, OnboardingTaskGraphEdge, OnboardingTaskItem } from '@/types/onboarding';

function stateLabel(state: string): string {
  return state.replace(/_/g, ' ');
}

function stateStyles(state: string): string {
  if (state === 'completed') return 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-200';
  if (state === 'requires_revision') return 'bg-amber-100 text-amber-950 dark:bg-amber-950/50 dark:text-amber-100';
  if (state === 'in_progress') return 'bg-sky-100 text-sky-900 dark:bg-sky-950/60 dark:text-sky-200';
  return 'bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400';
}

type Props = {
  orderedTasks: OnboardingTaskItem[];
  selectedId: string | null;
  onSelect: (nodeId: string) => void;
  byId: Map<string, OnboardingTaskItem>;
  edges: OnboardingTaskGraphEdge[];
  orderMode: FlowOrderMode;
  orderedIds: string[];
};

export function OnboardingTaskSidebar({
  orderedTasks,
  selectedId,
  onSelect,
  byId,
  edges,
  orderMode,
  orderedIds,
}: Props) {
  const { isEffectiveAdvanced: isAdvanced } = useScreenUiMode('prepare');
  return (
    <nav aria-label="Onboarding steps" className="space-y-1">
      {orderedTasks.map((t, index) => {
        const unlocked = isTaskUnlocked(t, byId, edges, orderedIds, orderMode);
        const active = selectedId === t.node_id;
        return (
          <button
            key={t.node_id}
            type="button"
            disabled={!unlocked}
            onClick={() => onSelect(t.node_id)}
            title={!unlocked ? 'Complete earlier steps first' : undefined}
            className={`flex w-full items-start gap-2 rounded-lg border px-3 py-2.5 text-left text-sm transition-colors ${
              active
                ? 'border-emerald-600 bg-emerald-50 dark:border-emerald-500 dark:bg-emerald-950/30'
                : 'border-transparent hover:bg-zinc-100 dark:hover:bg-zinc-800/80'
            } ${!unlocked ? 'cursor-not-allowed opacity-50' : ''}`}
          >
            <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-zinc-200 text-xs font-semibold text-zinc-700 dark:bg-zinc-700 dark:text-zinc-200">
              {index + 1}
            </span>
            <span className="min-w-0 flex-1">
              <span className="block font-medium text-zinc-900 dark:text-zinc-50">{t.title}</span>
              <span
                className={`mt-1 inline-block rounded-full px-2 py-0.5 text-[10px] font-medium capitalize ${stateStyles(t.state)}`}
              >
                {stateLabel(t.state)}
              </span>
              {isAdvanced && t.task_type ? (
                <span className="mt-1 block font-mono text-[10px] text-zinc-400">{t.task_type}</span>
              ) : null}
            </span>
          </button>
        );
      })}
    </nav>
  );
}
