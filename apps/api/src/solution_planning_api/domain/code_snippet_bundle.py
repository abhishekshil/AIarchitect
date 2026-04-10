"""Persisted architecture-aware code snippet bundle (Phase 12)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CodeSnippetBundleSummary(BaseModel):
    model_config = {"extra": "forbid"}

    bundle_id: UUID
    project_id: UUID
    runtime_graph_id: UUID | None = None
    runtime_graph_version: int = Field(ge=1)
    architecture_pattern: str
    created_at: datetime | None = None
