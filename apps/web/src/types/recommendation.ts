export type JsonObject = Record<string, unknown>;

export type ApiArchitectureRecommendationOption = {
  candidate_id: string;
  project_id: string;
  requirement_id: string;
  title: string;
  summary: string | null;
  score: number | null;
  rationale: string | null;
  tradeoffs: string[];
  assumptions: string[];
  complexity_estimate: JsonObject | null;
  latency_estimate: JsonObject | null;
  cost_estimate: JsonObject | null;
  governance_score: number | null;
  score_breakdown: JsonObject | null;
  capability_set: string[];
  architecture_template_ref: string | null;
  candidate_type: string | null;
  synthesized_graph: JsonObject;
};

export type ApiArchitectureRecommendationsEnvelope = {
  schema_version: '1.0';
  project_id: string;
  requirement_id: string | null;
  sort_mode: string;
  options: ApiArchitectureRecommendationOption[];
};

export const SCORING_MODES = ['best_overall', 'lowest_cost', 'fastest_launch', 'highest_quality'] as const;
export type ScoringMode = (typeof SCORING_MODES)[number];

export type ApiArchitectureSelection = {
  selection_id: string;
  project_id: string;
  requirement_id: string;
  solution_candidate_id: string;
  selected_at: string;
};

export type ApiTaskGraphNode = {
  node_id: string;
  title: string;
  description?: string | null;
  task_type?: string | null;
};

export type ApiTaskGraph = {
  task_graph_id: string;
  project_id: string;
  candidate_id?: string;
  nodes: ApiTaskGraphNode[];
  edges?: unknown[];
};

export type ApiArchitectureSelectionEnvelope = {
  schema_version: '1.0';
  selection: ApiArchitectureSelection;
  task_graph: ApiTaskGraph;
};
