"""Inference playground API shapes (Phase 11)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from solution_planning_api.domain import PlaygroundInferenceRun


class PlaygroundInferRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runtime_graph_version: int = Field(ge=1)
    input_text: str = Field(min_length=1, max_length=50_000)


class CitationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    citation_id: str
    source_ref: str
    snippet: str
    score: float


class TraceStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_index: int
    node_id: str | None = None
    component_type: str | None = None
    action: str
    detail: dict[str, Any] = Field(default_factory=dict)


class PlaygroundInferResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    inference_id: UUID
    runtime_graph_id: UUID
    runtime_graph_version: int
    architecture_pattern: str
    output_text: str
    structured_output: dict[str, Any] | None = None
    citations: list[CitationItem]
    traces: list[TraceStep]
    metadata: dict[str, Any]


class PlaygroundInferenceRunSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inference_id: UUID
    project_id: UUID
    runtime_graph_id: UUID | None = None
    runtime_graph_version: int
    architecture_pattern: str
    input_preview: str
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, run: PlaygroundInferenceRun) -> PlaygroundInferenceRunSummaryResponse:
        return cls(
            inference_id=run.inference_id,
            project_id=run.project_id,
            runtime_graph_id=run.runtime_graph_id,
            runtime_graph_version=run.runtime_graph_version,
            architecture_pattern=run.architecture_pattern,
            input_preview=run.input_preview,
            created_at=run.created_at,
        )


class PlaygroundInferenceHistoryEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    project_id: UUID
    runs: list[PlaygroundInferenceRunSummaryResponse]
