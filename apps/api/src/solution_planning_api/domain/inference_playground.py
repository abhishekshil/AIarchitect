"""Playground inference history rows (Phase 11)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PlaygroundInferenceRun(BaseModel):
    model_config = {"extra": "forbid"}

    inference_id: UUID
    project_id: UUID
    runtime_graph_id: UUID | None = None
    runtime_graph_version: int = Field(ge=1)
    architecture_pattern: str
    input_preview: str
    created_at: datetime | None = None
