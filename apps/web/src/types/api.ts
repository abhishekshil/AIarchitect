/** Mirrors FastAPI `UserResponse`. */
export type ApiUser = {
  user_id: string;
  email: string;
  created_at: string | null;
};

/** Mirrors FastAPI `TokenResponse`. */
export type ApiTokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
};

/** Mirrors FastAPI `ProjectResponse`. */
export type ApiProject = {
  project_id: string;
  owner_user_id: string;
  name: string;
  description: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type ApiErrorBody = {
  detail?: string | unknown[];
  code?: string;
};
