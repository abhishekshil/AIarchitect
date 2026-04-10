from __future__ import annotations

import json

from solution_planning_api.application.dto.code_snippets import SnippetGenerationContext
from solution_planning_api.infrastructure.snippets.hints import pattern_hint


def render_python_bundle(
    ctx: SnippetGenerationContext,
    *,
    example_request: dict,
    example_response: dict,
) -> str:
    pid = str(ctx.project_id)
    base = ctx.base_url.rstrip("/")
    payload_literal = repr(json.dumps(example_request))
    resp_literal = repr(json.dumps(example_response, indent=2))
    return f'''"""Inference playground client (stdlib only; no extra pip deps).

Architecture: {ctx.architecture_pattern} — {pattern_hint(ctx.architecture_pattern)}
"""
from __future__ import annotations

import json
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE_URL = "{base}"
PROJECT_ID = "{pid}"
ACCESS_TOKEN = "{ctx.token_placeholder}"  # JWT from POST /api/v1/auth/login


def playground_infer() -> dict:
    url = f"{{BASE_URL}}/api/v1/projects/{{PROJECT_ID}}/playground/infer"
    payload = {payload_literal}.encode("utf-8")
    req = Request(
        url,
        data=payload,
        headers={{
            "Authorization": f"Bearer {{ACCESS_TOKEN}}",
            "Content-Type": "application/json",
        }},
        method="POST",
    )
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        raise RuntimeError(e.read().decode("utf-8")) from e


def list_inference_runs() -> dict:
    url = f"{{BASE_URL}}/api/v1/projects/{{PROJECT_ID}}/playground/inference-runs"
    req = Request(
        url,
        headers={{"Authorization": f"Bearer {{ACCESS_TOKEN}}"}},
        method="GET",
    )
    with urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


# Example response shape (illustrative):
_EXAMPLE_RESPONSE = {resp_literal}
_ = _EXAMPLE_RESPONSE  # documentation anchor for readers
'''
