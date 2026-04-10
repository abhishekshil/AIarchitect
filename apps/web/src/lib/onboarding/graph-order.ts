import type { OnboardingTaskGraphEdge } from '@/types/onboarding';

/**
 * Topological order of node ids (Kahn). Unknown nodes in edges are skipped.
 * Remaining ids (cycles or disconnected) are appended in `fallback` order.
 */
export function topologicalOrder(
  nodeIds: string[],
  edges: OnboardingTaskGraphEdge[],
  fallback: string[],
): string[] {
  const nodes = new Set(nodeIds);
  const inDegree = new Map<string, number>();
  const outgoing = new Map<string, string[]>();

  for (const id of nodeIds) {
    inDegree.set(id, 0);
    outgoing.set(id, []);
  }

  for (const e of edges) {
    if (!nodes.has(e.source_id) || !nodes.has(e.target_id)) continue;
    outgoing.get(e.source_id)!.push(e.target_id);
    inDegree.set(e.target_id, (inDegree.get(e.target_id) ?? 0) + 1);
  }

  const queue: string[] = [];
  for (const [id, d] of inDegree) {
    if (d === 0) queue.push(id);
  }

  const ordered: string[] = [];
  while (queue.length) {
    const u = queue.shift()!;
    ordered.push(u);
    for (const v of outgoing.get(u) ?? []) {
      const next = (inDegree.get(v) ?? 0) - 1;
      inDegree.set(v, next);
      if (next === 0) queue.push(v);
    }
  }

  const seen = new Set(ordered);
  for (const id of fallback) {
    if (nodes.has(id) && !seen.has(id)) ordered.push(id);
  }
  return ordered;
}
