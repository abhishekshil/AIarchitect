"""Async runtime graph build job tracking (Phase 10)."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field


class RuntimeBuildJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class RuntimeBuildJob(BaseModel):
    model_config = {"extra": "forbid"}

    job_id: UUID
    project_id: UUID
    requirement_id: UUID | None = None
    solution_candidate_id: UUID | None = None
    status: RuntimeBuildJobStatus
    stage: str = Field(default="queued", description="Current pipeline stage for UX/debug.")
    error_detail: str | None = None
    runtime_graph_id: UUID | None = None
    runtime_graph_version: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
