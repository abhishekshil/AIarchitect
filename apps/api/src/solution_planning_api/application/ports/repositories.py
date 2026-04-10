"""
Repository ports — implemented in infrastructure in later phases.

These protocols keep domain/application free of SQLAlchemy imports.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from solution_planning_api.application.dto.requirement import RequirementRevision
from solution_planning_api.application.unset import UnsetType
from solution_planning_api.domain import (
    ArchitectureSelection,
    CodeSnippetBundleSummary,
    ConstraintProfile,
    OnboardingTaskProgress,
    OnboardingTaskState,
    PlaygroundInferenceRun,
    Project,
    RequirementProfile,
    RuntimeBuildJob,
    RuntimeBuildJobStatus,
    RuntimeGraph,
    SolutionCandidate,
    TaskGraph,
    User,
)
from solution_planning_api.domain.scoring import ScoringMode


class UserRepository(Protocol):
    async def create(self, *, email: str, password_hash: str) -> User: ...
    async def get_by_id(self, user_id: UUID) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...


class ProjectRepository(Protocol):
    async def create(
        self, *, owner_user_id: UUID, name: str, description: str | None
    ) -> Project: ...
    async def get_by_id(self, project_id: UUID) -> Project | None: ...
    async def list_for_user(self, user_id: UUID) -> list[Project]: ...
    async def update(
        self,
        *,
        project_id: UUID,
        owner_user_id: UUID,
        name: str | None | UnsetType,
        description: str | None | UnsetType,
    ) -> Project | None: ...
    async def delete(self, *, project_id: UUID, owner_user_id: UUID) -> bool: ...


class RequirementProfileRepository(Protocol):
    async def next_version(self, project_id: UUID) -> int: ...

    async def create(
        self, *, project_id: UUID, version: int, profile: RequirementProfile
    ) -> RequirementRevision: ...

    async def get_by_id(self, requirement_id: UUID) -> RequirementRevision | None: ...

    async def get_latest_for_project(self, project_id: UUID) -> RequirementRevision | None: ...

    async def list_for_project(self, project_id: UUID) -> list[RequirementRevision]: ...


class ConstraintProfileRepository(Protocol):
    async def create(
        self, *, project_id: UUID, requirement_profile_id: UUID, profile: ConstraintProfile
    ) -> ConstraintProfile: ...

    async def get_for_requirement(self, requirement_id: UUID) -> ConstraintProfile | None: ...


class SolutionCandidateRepository(Protocol):
    async def create_in_batch(
        self,
        *,
        project_id: UUID,
        requirement_profile_id: UUID,
        generation_batch_id: UUID,
        candidates: list[SolutionCandidate],
    ) -> list[SolutionCandidate]: ...

    async def list_latest_batch(
        self,
        requirement_profile_id: UUID,
        *,
        sort_mode: ScoringMode,
    ) -> list[SolutionCandidate]: ...

    async def get_by_id(self, project_id: UUID, candidate_id: UUID) -> SolutionCandidate | None: ...


class ArchitectureSelectionRepository(Protocol):
    async def replace_for_requirement(
        self,
        *,
        project_id: UUID,
        requirement_profile_id: UUID,
        solution_candidate_id: UUID,
    ) -> ArchitectureSelection: ...

    async def get_latest_for_requirement(
        self, requirement_profile_id: UUID
    ) -> ArchitectureSelection | None: ...


class TaskGraphRepository(Protocol):
    async def upsert_for_candidate(
        self,
        *,
        project_id: UUID,
        solution_candidate_id: UUID,
        graph: TaskGraph,
    ) -> TaskGraph: ...

    async def get_for_candidate(
        self, project_id: UUID, solution_candidate_id: UUID
    ) -> TaskGraph | None: ...


class OnboardingProgressRepository(Protocol):
    async def list_for_task_graph(self, task_graph_id: UUID) -> list[OnboardingTaskProgress]: ...

    async def upsert(
        self,
        *,
        project_id: UUID,
        requirement_profile_id: UUID,
        task_graph_id: UUID,
        node_id: str,
        state: OnboardingTaskState,
        response: dict[str, object] | None,
        validation_feedback: dict[str, object] | None,
    ) -> OnboardingTaskProgress: ...

    async def delete_for_requirement_except_graph(
        self, requirement_profile_id: UUID, keep_task_graph_id: UUID
    ) -> None: ...


class RuntimeGraphRepository(Protocol):
    async def next_version(self, project_id: UUID) -> int: ...

    async def create(
        self,
        *,
        project_id: UUID,
        solution_candidate_id: UUID | None,
        version: int,
        graph: RuntimeGraph,
    ) -> RuntimeGraph: ...

    async def get_by_version(self, project_id: UUID, version: int) -> RuntimeGraph | None: ...

    async def list_version_summaries(
        self, project_id: UUID
    ) -> list[tuple[int, UUID, datetime]]: ...


class RuntimeBuildJobRepository(Protocol):
    async def create_pending(
        self,
        *,
        project_id: UUID,
        requirement_id: UUID | None,
        solution_candidate_id: UUID | None,
    ) -> RuntimeBuildJob: ...

    async def get(self, project_id: UUID, job_id: UUID) -> RuntimeBuildJob | None: ...

    async def get_by_id(self, job_id: UUID) -> RuntimeBuildJob | None: ...

    async def update(
        self,
        job_id: UUID,
        *,
        status: RuntimeBuildJobStatus | None = None,
        stage: str | None = None,
        error_detail: str | None = None,
        runtime_graph_id: UUID | None = None,
        runtime_graph_version: int | None = None,
    ) -> None: ...


class PlaygroundInferenceRepository(Protocol):
    async def create_run(
        self,
        *,
        inference_id: UUID,
        project_id: UUID,
        runtime_graph_id: UUID | None,
        runtime_graph_version: int,
        architecture_pattern: str,
        input_text: str,
        request_payload: dict[str, Any],
        response_payload: dict[str, Any],
    ) -> PlaygroundInferenceRun: ...

    async def list_runs(self, project_id: UUID, *, limit: int = 50) -> list[PlaygroundInferenceRun]: ...

    async def get_response_payload(
        self, project_id: UUID, inference_id: UUID
    ) -> dict[str, Any] | None: ...


class CodeSnippetBundleRepository(Protocol):
    async def create_bundle(
        self,
        *,
        bundle_id: UUID,
        project_id: UUID,
        runtime_graph_id: UUID | None,
        runtime_graph_version: int,
        architecture_pattern: str,
        payload: dict[str, Any],
    ) -> CodeSnippetBundleSummary: ...

    async def list_bundles(self, project_id: UUID, *, limit: int = 20) -> list[CodeSnippetBundleSummary]: ...

    async def get_payload(self, project_id: UUID, bundle_id: UUID) -> dict[str, Any] | None: ...
