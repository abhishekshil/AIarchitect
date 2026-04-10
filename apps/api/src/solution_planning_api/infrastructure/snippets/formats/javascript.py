from __future__ import annotations

import json

from solution_planning_api.application.dto.code_snippets import SnippetGenerationContext
from solution_planning_api.infrastructure.snippets.hints import pattern_hint


def render_javascript_bundle(
    ctx: SnippetGenerationContext,
    *,
    example_request: dict,
    example_response: dict,
) -> str:
    pid = str(ctx.project_id)
    base = ctx.base_url.rstrip("/")
    infer_body = json.dumps(example_request)
    resp_json = json.dumps(example_response, indent=2)
    return f"""// Architecture: {ctx.architecture_pattern} — {pattern_hint(ctx.architecture_pattern)}
// Requires: browser fetch or Node 18+ (global fetch). For Node <18, use undici or node-fetch.

const BASE_URL = "{base}";
const PROJECT_ID = "{pid}";
const ACCESS_TOKEN = "{ctx.token_placeholder}"; // replace with JWT

const inferBody = {infer_body};

async function runInfer() {{
  const res = await fetch(
    `${{BASE_URL}}/api/v1/projects/${{PROJECT_ID}}/playground/infer`,
    {{
      method: "POST",
      headers: {{
        Authorization: `Bearer ${{ACCESS_TOKEN}}`,
        "Content-Type": "application/json",
      }},
      body: JSON.stringify(inferBody),
    }}
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}}

async function listRuns() {{
  const res = await fetch(
    `${{BASE_URL}}/api/v1/projects/${{PROJECT_ID}}/playground/inference-runs`,
    {{ headers: {{ Authorization: `Bearer ${{ACCESS_TOKEN}}` }} }}
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}}

// Example response (illustrative):
const exampleResponse = {resp_json};
void exampleResponse;

export {{ runInfer, listRuns }};
"""

