export type OnboardingTaskState =
  | 'not_started'
  | 'in_progress'
  | 'submitted'
  | 'validated'
  | 'requires_revision'
  | 'completed';

export type OnboardingTaskItem = {
  node_id: string;
  title: string;
  description: string | null;
  task_type: string | null;
  metadata: Record<string, unknown> | null;
  guidance_refs: string[];
  condition: string | null;
  state: OnboardingTaskState;
  suggestions: string[];
  example_placeholder: string;
  response: Record<string, unknown> | null;
  validation_feedback: OnboardingValidationFeedback | null;
  updated_at: string | null;
};

export type OnboardingValidationFeedback = {
  status?: string;
  errors?: string[];
  warnings?: string[];
  pipeline?: string[];
};

export type OnboardingTaskGraphEdge = {
  source_id: string;
  target_id: string;
  relation: string | null;
};

export type OnboardingTasksEnvelope = {
  schema_version: '1.0';
  task_graph_id: string;
  tasks: OnboardingTaskItem[];
  edges: OnboardingTaskGraphEdge[];
};

export type OnboardingProgress = {
  schema_version: '1.0';
  task_graph_id: string;
  total_tasks: number;
  by_state: Record<string, number>;
  percent_completed: number;
};

export type FlowOrderMode = 'linear' | 'graph';
