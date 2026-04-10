"""Stable endpoint metadata for snippet generation and future SDK OpenAPI sync."""

from __future__ import annotations

from typing import Any


def playground_endpoint_metadata() -> list[dict[str, Any]]:
    return [
        {
            "name": "playground_test",
            "method": "GET",
            "path": "/api/v1/projects/{project_id}/playground/test",
            "description": "Verify playground routes and project access.",
        },
        {
            "name": "playground_infer",
            "method": "POST",
            "path": "/api/v1/projects/{project_id}/playground/infer",
            "description": "Run inference against a versioned runtime graph (mock engine in Phase 11).",
        },
        {
            "name": "playground_inference_runs",
            "method": "GET",
            "path": "/api/v1/projects/{project_id}/playground/inference-runs",
            "description": "List recent inference runs for this project.",
        },
        {
            "name": "playground_inference_detail",
            "method": "GET",
            "path": "/api/v1/projects/{project_id}/playground/inference-runs/{inference_id}",
            "description": "Fetch a single persisted inference response payload.",
        },
    ]
