"""Build a JSON-serializable snippet bundle payload for persistence and API responses."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from solution_planning_api.application.dto.code_snippets import SnippetGenerationContext
from solution_planning_api.infrastructure.snippets.endpoints import playground_endpoint_metadata
from solution_planning_api.infrastructure.snippets.examples import playground_example_for_pattern
from solution_planning_api.infrastructure.snippets.formats import FORMAT_RENDERERS
from solution_planning_api.infrastructure.snippets.hints import pattern_hint


def assemble_snippet_bundle_payload(*, bundle_id: UUID, ctx: SnippetGenerationContext) -> dict[str, Any]:
    pid = str(ctx.project_id)
    example_request, example_response = playground_example_for_pattern(
        architecture_pattern=ctx.architecture_pattern,
        project_id_str=pid,
        runtime_graph_version=ctx.runtime_graph_version,
    )
    snippets = {
        name: render(ctx, example_request=example_request, example_response=example_response)
        for name, render in sorted(FORMAT_RENDERERS.items())
    }
    env_notes = "\n".join(
        [
            f"- Base URL for requests: {ctx.base_url} (override with PUBLIC_API_BASE_URL in server env for accurate links).",
            f"- Authenticate with Bearer JWT from POST /api/v1/auth/login using the same API origin.",
            f"- This bundle targets runtime_graph_version={ctx.runtime_graph_version} for project {pid}.",
            f"- Detected architecture_pattern={ctx.architecture_pattern}: {pattern_hint(ctx.architecture_pattern)}",
        ]
    )
    if ctx.architecture_template_id:
        env_notes += f"\n- Template id from graph bindings: {ctx.architecture_template_id}"

    return {
        "schema_version": "1.0",
        "bundle_id": str(bundle_id),
        "project_id": pid,
        "runtime_graph_id": str(ctx.runtime_graph_id),
        "runtime_graph_version": ctx.runtime_graph_version,
        "architecture_pattern": ctx.architecture_pattern,
        "environment_notes": env_notes,
        "endpoint_metadata": playground_endpoint_metadata(),
        "example_request": example_request,
        "example_response": example_response,
        "snippets": snippets,
    }
