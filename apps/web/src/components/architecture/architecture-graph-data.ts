import type { ApiArchitectureRecommendationOption } from '@/types/recommendation';

export type GraphNode = {
  id: string;
  label: string;
};

export type GraphEdge = {
  source: string;
  target: string;
};

const MAX_GRAPH_NODES = 20;

function asObject(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  return value as Record<string, unknown>;
}

function getString(value: unknown): string | null {
  return typeof value === 'string' && value.trim().length > 0 ? value.trim() : null;
}

export function parseArchitectureGraph(
  option: ApiArchitectureRecommendationOption,
  maxNodes = MAX_GRAPH_NODES,
): { nodes: GraphNode[]; edges: GraphEdge[] } {
  const synthesized = asObject(option.synthesized_graph);
  const nodesRaw = Array.isArray(synthesized?.nodes) ? synthesized.nodes : [];
  const edgesRaw = Array.isArray(synthesized?.edges) ? synthesized.edges : [];

  const nodes: GraphNode[] = [];
  for (const item of nodesRaw) {
    const obj = asObject(item);
    if (!obj) continue;
    const id =
      getString(obj.id) ??
      getString(obj.node_id) ??
      getString(obj.key) ??
      getString(obj.name) ??
      getString(obj.title) ??
      getString(obj.label);
    if (!id) continue;
    const label = getString(obj.label) ?? getString(obj.title) ?? getString(obj.name) ?? id;
    if (!nodes.some((n) => n.id === id)) nodes.push({ id, label });
    if (nodes.length >= maxNodes) break;
  }

  const nodeIds = new Set(nodes.map((n) => n.id));
  const edges: GraphEdge[] = [];
  for (const item of edgesRaw) {
    const obj = asObject(item);
    if (!obj) continue;
    const source = getString(obj.source) ?? getString(obj.from) ?? getString(obj.src);
    const target = getString(obj.target) ?? getString(obj.to) ?? getString(obj.dst);
    if (!source || !target) continue;
    if (nodeIds.has(source) && nodeIds.has(target)) edges.push({ source, target });
  }

  if (nodes.length >= 2) return { nodes, edges };

  const capabilityNodes = option.capability_set
    .slice(0, Math.max(0, maxNodes - 3))
    .map((capability, index) => ({ id: `cap-${index}`, label: capability.replace(/_/g, ' ') }));
  const fallbackNodes: GraphNode[] = [
    { id: 'input', label: 'User requirement' },
    { id: 'planner', label: option.title || 'Solution planner' },
    ...capabilityNodes,
    { id: 'output', label: 'Deployed architecture' },
  ].slice(0, maxNodes);

  const fallbackEdges: GraphEdge[] = [];
  for (let i = 0; i < fallbackNodes.length - 1; i += 1) {
    fallbackEdges.push({ source: fallbackNodes[i].id, target: fallbackNodes[i + 1].id });
  }
  return { nodes: fallbackNodes, edges: fallbackEdges };
}

export function truncateGraphLabel(label: string, max = 20): string {
  if (label.length <= max) return label;
  return `${label.slice(0, max - 1)}…`;
}
