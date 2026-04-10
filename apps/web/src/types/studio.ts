/** Runtime build + playground + snippets (Phase 17). */

export type RuntimeBuildJobResponse = {
  schema_version: '1.0';
  job_id: string;
  project_id: string;
  requirement_id: string | null;
  solution_candidate_id: string | null;
  status: string;
  stage: string;
  error_detail: string | null;
  runtime_graph_id: string | null;
  runtime_graph_version: number | null;
  created_at: string | null;
  updated_at: string | null;
};

export type RuntimeGraphVersionSummary = {
  version: number;
  runtime_graph_id: string;
  created_at: string;
};

export type RuntimeGraphListEnvelope = {
  schema_version: '1.0';
  project_id: string;
  versions: RuntimeGraphVersionSummary[];
};

export type PlaygroundCitation = {
  citation_id: string;
  source_ref: string;
  snippet: string;
  score: number;
};

export type PlaygroundTrace = {
  step_index: number;
  node_id: string | null;
  component_type: string | null;
  action: string;
  detail: Record<string, unknown>;
};

export type PlaygroundInferResponse = {
  schema_version: '1.0';
  inference_id: string;
  runtime_graph_id: string;
  runtime_graph_version: number;
  architecture_pattern: string;
  output_text: string;
  structured_output: Record<string, unknown> | null;
  citations: PlaygroundCitation[];
  traces: PlaygroundTrace[];
  metadata: Record<string, unknown>;
};

export type PlaygroundInferenceRunSummary = {
  inference_id: string;
  project_id: string;
  runtime_graph_id: string | null;
  runtime_graph_version: number;
  architecture_pattern: string;
  input_preview: string;
  created_at: string | null;
};

export type PlaygroundInferenceHistoryEnvelope = {
  schema_version: '1.0';
  project_id: string;
  runs: PlaygroundInferenceRunSummary[];
};

export type SnippetEndpointMeta = {
  name: string;
  method: string;
  path: string;
  description: string | null;
};

export type CodeSnippetBundleResponse = {
  schema_version: '1.0';
  bundle_id: string;
  project_id: string;
  runtime_graph_id: string;
  runtime_graph_version: number;
  architecture_pattern: string;
  environment_notes: string;
  endpoint_metadata: SnippetEndpointMeta[];
  example_request: Record<string, unknown>;
  example_response: Record<string, unknown>;
  snippets: Record<string, string>;
};

export type CodeSnippetBundleSummary = {
  bundle_id: string;
  project_id: string;
  runtime_graph_id: string | null;
  runtime_graph_version: number;
  architecture_pattern: string;
  created_at: string | null;
};

export type CodeSnippetBundleListEnvelope = {
  schema_version: '1.0';
  project_id: string;
  bundles: CodeSnippetBundleSummary[];
};

export const SNIPPET_LANGUAGES = ['curl', 'javascript', 'python'] as const;
export type SnippetLanguage = (typeof SNIPPET_LANGUAGES)[number];

export type StudioTabId = 'build' | 'playground' | 'integration';
