from __future__ import annotations

import json

from solution_planning_api.application.dto.code_snippets import SnippetGenerationContext
from solution_planning_api.infrastructure.snippets.hints import pattern_hint


def render_curl_bundle(
    ctx: SnippetGenerationContext,
    *,
    example_request: dict,
    example_response: dict,
) -> str:
    pid = str(ctx.project_id)
    base = ctx.base_url.rstrip("/")
    infer_url = f"{base}/api/v1/projects/{pid}/playground/infer"
    runs_url = f"{base}/api/v1/projects/{pid}/playground/inference-runs"
    body = json.dumps(example_request, separators=(",", ":"))
    ex_resp = json.dumps(example_response, indent=2)
    return f"""# Environment: set {ctx.token_placeholder} to a JWT from POST /api/v1/auth/login (or register + login).
# Base URL: {base}
# Runtime graph version used below: {ctx.runtime_graph_version}
# Architecture pattern: {ctx.architecture_pattern} — {pattern_hint(ctx.architecture_pattern)}

# --- Run inference (primary testing path) ---
curl -sS -X POST "{infer_url}" \\
  -H "Authorization: Bearer {ctx.token_placeholder}" \\
  -H "Content-Type: application/json" \\
  -d '{body}'

# --- List recent inference runs ---
curl -sS "{runs_url}" \\
  -H "Authorization: Bearer {ctx.token_placeholder}"

# Example response shape (illustrative; IDs and text will differ):
# {ex_resp}
"""

