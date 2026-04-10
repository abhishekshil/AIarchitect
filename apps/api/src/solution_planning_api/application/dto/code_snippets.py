"""Inputs for code snippet generation (Phase 12)."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SnippetGenerationContext:
    """Stable contract for format renderers; SDKs can reuse the same context."""

    base_url: str
    project_id: UUID
    runtime_graph_id: UUID
    runtime_graph_version: int
    architecture_pattern: str
    architecture_template_id: str | None
    token_placeholder: str = "$ACCESS_TOKEN"
