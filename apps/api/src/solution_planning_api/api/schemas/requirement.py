from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from solution_planning_api.application.dto.requirement import (
    RequirementRevision,
    RequirementSubmissionResult,
)
from solution_planning_api.domain import ConstraintProfile, RequirementProfile


class RequirementSubmitRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    raw_text: str = Field(..., min_length=1, max_length=50_000)


class RequirementRevisionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_id: UUID
    project_id: UUID
    version: int
    created_at: datetime
    profile: RequirementProfile


class NormalizationInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    method: str
    rationale: list[str]


class RequirementSubmitResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: RequirementRevisionResponse
    constraint_profile: ConstraintProfile | None = None
    normalization: NormalizationInfo
    clarification_questions: list[str] = Field(default_factory=list)
    normalization_audit: dict[str, object] = Field(default_factory=dict)


class RequirementSummaryResponse(BaseModel):
    """List view — avoids huge payloads for long raw_text (truncate in API layer)."""

    model_config = ConfigDict(extra="forbid")

    requirement_id: UUID
    project_id: UUID
    version: int
    created_at: datetime
    raw_text_preview: str
    primary_task_type: str | None
    confidence_score: float | None


class RequirementDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revision: RequirementRevisionResponse
    constraint_profile: ConstraintProfile | None = None


def revision_to_response(rev: RequirementRevision) -> RequirementRevisionResponse:
    return RequirementRevisionResponse(
        requirement_id=rev.requirement_id,
        project_id=rev.project_id,
        version=rev.version,
        created_at=rev.created_at,
        profile=rev.profile,
    )


def submission_to_response(result: RequirementSubmissionResult) -> RequirementSubmitResponse:
    return RequirementSubmitResponse(
        revision=revision_to_response(result.revision),
        constraint_profile=result.constraint_profile,
        normalization=NormalizationInfo(
            method=result.normalization_method,
            rationale=result.normalization_rationale,
        ),
        clarification_questions=result.clarification_questions,
        normalization_audit=result.normalization_audit,
    )


def revision_to_summary(rev: RequirementRevision, *, preview_len: int = 240) -> RequirementSummaryResponse:
    text = rev.profile.raw_text
    preview = text if len(text) <= preview_len else text[: preview_len - 1] + "…"
    return RequirementSummaryResponse(
        requirement_id=rev.requirement_id,
        project_id=rev.project_id,
        version=rev.version,
        created_at=rev.created_at,
        raw_text_preview=preview,
        primary_task_type=rev.profile.primary_task_type,
        confidence_score=rev.profile.confidence_score,
    )
