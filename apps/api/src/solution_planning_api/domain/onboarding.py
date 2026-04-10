"""Onboarding task lifecycle (Phase 9)."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from solution_planning_api.domain.common import JsonObject


class OnboardingTaskState(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    REQUIRES_REVISION = "requires_revision"
    COMPLETED = "completed"


class OnboardingTaskProgress(BaseModel):
    """Persisted progress row for one graph node."""

    model_config = {"extra": "forbid"}

    progress_id: UUID
    project_id: UUID
    requirement_id: UUID
    task_graph_id: UUID
    node_id: str
    state: OnboardingTaskState
    response: JsonObject | None = None
    validation_feedback: JsonObject | None = None
    updated_at: datetime | None = None
