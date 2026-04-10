import type { FlowOrderMode, OnboardingTaskGraphEdge, OnboardingTaskItem } from '@/types/onboarding';

function isCompleted(t: OnboardingTaskItem): boolean {
  return t.state === 'completed';
}

/** Whether the user may open and work on this task given ordering rules. */
export function isTaskUnlocked(
  task: OnboardingTaskItem,
  byId: Map<string, OnboardingTaskItem>,
  edges: OnboardingTaskGraphEdge[],
  orderedIds: string[],
  mode: FlowOrderMode,
): boolean {
  if (isCompleted(task)) return true;

  if (mode === 'linear') {
    const idx = orderedIds.indexOf(task.node_id);
    if (idx <= 0) return true;
    for (let i = 0; i < idx; i++) {
      const prev = byId.get(orderedIds[i]);
      if (prev && !isCompleted(prev)) return false;
    }
    return true;
  }

  const preds = edges.filter((e) => e.target_id === task.node_id).map((e) => e.source_id);
  if (preds.length === 0) return true;
  for (const p of preds) {
    const pt = byId.get(p);
    if (!pt || !isCompleted(pt)) return false;
  }
  return true;
}
