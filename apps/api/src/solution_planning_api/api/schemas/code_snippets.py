"""API models for generated client snippets (Phase 12)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from solution_planning_api.domain import CodeSnippetBundleSummary


class GenerateCodeSnippetsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runtime_graph_version: int | None = Field(
        default=None,
        ge=1,
        description="When omitted, the latest runtime graph version for the project is used.",
    )


class SnippetEndpointMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    method: str
    path: str
    description: str | None = None


class CodeSnippetBundleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    bundle_id: UUID
    project_id: UUID
    runtime_graph_id: UUID
    runtime_graph_version: int
    architecture_pattern: str
    environment_notes: str
    endpoint_metadata: list[SnippetEndpointMeta]
    example_request: dict[str, Any]
    example_response: dict[str, Any]
    snippets: dict[str, str]


class CodeSnippetBundleSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bundle_id: UUID
    project_id: UUID
    runtime_graph_id: UUID | None = None
    runtime_graph_version: int
    architecture_pattern: str
    created_at: datetime | None = None

    @classmethod
    def from_domain(cls, row: CodeSnippetBundleSummary) -> CodeSnippetBundleSummaryResponse:
        return cls(
            bundle_id=row.bundle_id,
            project_id=row.project_id,
            runtime_graph_id=row.runtime_graph_id,
            runtime_graph_version=row.runtime_graph_version,
            architecture_pattern=row.architecture_pattern,
            created_at=row.created_at,
        )


class CodeSnippetBundleListEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    project_id: UUID
    bundles: list[CodeSnippetBundleSummaryResponse]
