"""Architecture-aware evaluation / test plan (Blueprint §11.8, §13)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from solution_planning_api.domain.common import JsonObject


class MetricThreshold(BaseModel):
    model_config = {"extra": "forbid"}

    metric: str
    threshold: float | str
    comparator: str | None = "gte"


class EvaluationSuite(BaseModel):
    model_config = {"extra": "forbid"}

    suite_id: str
    name: str
    test_types: list[str] = Field(default_factory=list)
    metrics: list[MetricThreshold] = Field(default_factory=list)
    acceptance_notes: str | None = None


class EvaluationPlan(BaseModel):
    model_config = {"extra": "forbid"}

    evaluation_plan_id: UUID
    project_id: UUID
    candidate_id: UUID | None = None

    suites: list[EvaluationSuite] = Field(default_factory=list)
    global_thresholds: JsonObject | None = None
    metadata: JsonObject | None = None
