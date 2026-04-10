from __future__ import annotations

from uuid import UUID

from solution_planning_api.application.dto.requirement import (
    RequirementRevision,
    RequirementSubmissionResult,
)
from solution_planning_api.application.errors import NotFoundError
from solution_planning_api.application.ports.repositories import (
    ConstraintProfileRepository,
    RequirementProfileRepository,
)
from solution_planning_api.application.ports.requirement_normalization import (
    NormalizationContext,
    RequirementNormalizer,
)
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.domain import ConstraintProfile


class RequirementService:
    def __init__(
        self,
        projects: ProjectService,
        requirements: RequirementProfileRepository,
        constraints: ConstraintProfileRepository,
        normalizer: RequirementNormalizer,
    ) -> None:
        self._projects = projects
        self._requirements = requirements
        self._constraints = constraints
        self._normalizer = normalizer

    async def submit_raw_requirement(
        self, *, owner_user_id: UUID, project_id: UUID, raw_text: str
    ) -> RequirementSubmissionResult:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)

        ctx = NormalizationContext(
            project_id=project_id,
            owner_user_id=owner_user_id,
            raw_text=raw_text,
        )
        normalized = await self._normalizer.normalize(ctx)

        version = await self._requirements.next_version(project_id)
        revision = await self._requirements.create(
            project_id=project_id,
            version=version,
            profile=normalized.requirement_profile,
        )

        constraint = None
        if normalized.constraint_profile is not None:
            constraint = await self._constraints.create(
                project_id=project_id,
                requirement_profile_id=revision.requirement_id,
                profile=normalized.constraint_profile,
            )

        return RequirementSubmissionResult(
            revision=revision,
            constraint_profile=constraint,
            normalization_method=normalized.method,
            normalization_rationale=normalized.rationale,
            clarification_questions=normalized.clarification_questions,
            normalization_audit=normalized.audit,
        )

    async def get_requirement(
        self, *, owner_user_id: UUID, project_id: UUID, requirement_id: UUID
    ) -> RequirementRevision:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        rev = await self._requirements.get_by_id(requirement_id)
        if rev is None or rev.project_id != project_id:
            raise NotFoundError("Requirement not found", code="requirement_not_found")
        return rev

    async def get_latest_requirement(
        self, *, owner_user_id: UUID, project_id: UUID
    ) -> RequirementRevision:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        rev = await self._requirements.get_latest_for_project(project_id)
        if rev is None:
            raise NotFoundError("No requirements for this project", code="requirement_not_found")
        return rev

    async def list_requirements(
        self, *, owner_user_id: UUID, project_id: UUID
    ) -> list[RequirementRevision]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        return await self._requirements.list_for_project(project_id)

    async def get_constraint_for_requirement(
        self, *, owner_user_id: UUID, project_id: UUID, requirement_id: UUID
    ) -> ConstraintProfile | None:
        rev = await self.get_requirement(
            owner_user_id=owner_user_id,
            project_id=project_id,
            requirement_id=requirement_id,
        )
        return await self._constraints.get_for_requirement(rev.requirement_id)
