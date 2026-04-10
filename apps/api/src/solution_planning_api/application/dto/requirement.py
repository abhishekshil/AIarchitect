"""Read models for requirement revisions (DB metadata + domain profile)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from solution_planning_api.domain import ConstraintProfile, RequirementProfile


@dataclass(frozen=True)
class RequirementRevision:
    """One persisted requirement snapshot with versioning metadata."""

    requirement_id: UUID
    project_id: UUID
    version: int
    created_at: datetime
    profile: RequirementProfile


@dataclass(frozen=True)
class RequirementSubmissionResult:
    """Outcome of intake + normalization + persistence."""

    revision: RequirementRevision
    constraint_profile: ConstraintProfile | None
    normalization_method: str
    normalization_rationale: list[str]
    clarification_questions: list[str]
    normalization_audit: dict[str, object]
