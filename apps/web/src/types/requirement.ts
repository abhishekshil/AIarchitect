/** Mirrors FastAPI `RequirementSummaryResponse` (list view). */
export type ApiRequirementSummary = {
  requirement_id: string;
  project_id: string;
  version: number;
  created_at: string;
  raw_text_preview: string;
  primary_task_type: string | null;
  confidence_score: number | null;
};

/** Mirrors requirement profile inside `RequirementRevisionResponse`. */
export type ApiRequirementProfile = {
  requirement_id: string;
  project_id: string;
  raw_text: string;
  business_goal?: string | null;
  primary_task_type?: string | null;
  secondary_task_types?: string[];
  confidence_score?: number | null;
  success_criteria?: string[];
};

export type ApiRequirementRevisionResponse = {
  requirement_id: string;
  project_id: string;
  version: number;
  created_at: string;
  profile: ApiRequirementProfile;
};

export type ApiNormalizationInfo = {
  method: string;
  rationale: string[];
};

export type ApiRequirementSubmitResponse = {
  revision: ApiRequirementRevisionResponse;
  constraint_profile: Record<string, unknown> | null;
  normalization: ApiNormalizationInfo;
};
