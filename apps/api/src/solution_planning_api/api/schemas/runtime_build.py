"""Runtime build job + versioned runtime graph API (Phase 10)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from solution_planning_api.domain import RuntimeBuildJob, RuntimeGraph


class RuntimeBuildJobResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    job_id: UUID
    project_id: UUID
    requirement_id: UUID | None = None
    solution_candidate_id: UUID | None = None
    status: str
    stage: str
    error_detail: str | None = None
    runtime_graph_id: UUID | None = None
    runtime_graph_version: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @classmethod
    def from_domain(cls, job: RuntimeBuildJob) -> RuntimeBuildJobResponse:
        return cls(
            job_id=job.job_id,
            project_id=job.project_id,
            requirement_id=job.requirement_id,
            solution_candidate_id=job.solution_candidate_id,
            status=job.status.value,
            stage=job.stage,
            error_detail=job.error_detail,
            runtime_graph_id=job.runtime_graph_id,
            runtime_graph_version=job.runtime_graph_version,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )


class RuntimeGraphVersionSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int
    runtime_graph_id: UUID
    created_at: datetime


class RuntimeGraphListEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    project_id: UUID
    versions: list[RuntimeGraphVersionSummaryResponse]


class RuntimeGraphDetailEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    project_id: UUID
    graph: RuntimeGraph
