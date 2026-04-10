"""Integration-ready delivery bundle (Blueprint §11.9)."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from solution_planning_api.domain.common import JsonObject


class CodeSnippet(BaseModel):
    model_config = {"extra": "forbid"}

    snippet_id: str
    language: str
    title: str | None = None
    code: str
    path_hint: str | None = None


class EndpointDefinition(BaseModel):
    model_config = {"extra": "forbid"}

    name: str
    method: str | None = None
    path: str | None = None
    description: str | None = None
    schema_ref: str | None = None


class IntegrationPackage(BaseModel):
    model_config = {"extra": "forbid"}

    package_id: UUID
    project_id: UUID
    candidate_id: UUID | None = None

    code_snippets: list[CodeSnippet] = Field(default_factory=list)
    endpoint_definitions: list[EndpointDefinition] = Field(default_factory=list)
    setup_instructions: str | None = None
    sample_usage: JsonObject | None = None
    metadata: JsonObject | None = None
