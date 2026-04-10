from __future__ import annotations

import uuid
from uuid import UUID

from solution_planning_api.application.errors import NotFoundError
from solution_planning_api.application.ports.candidate_planning import CandidatePlanningEngine
from solution_planning_api.application.ports.registries import (
    ArchitectureTemplateRegistryReader,
    CapabilityRegistryReader,
)
from solution_planning_api.application.ports.repositories import (
    ConstraintProfileRepository,
    RequirementProfileRepository,
    SolutionCandidateRepository,
)
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.domain import SolutionCandidate
from solution_planning_api.domain.scoring import ScoringMode


def _sort_key(candidate: SolutionCandidate, mode: ScoringMode) -> float:
    breakdown = candidate.score_breakdown or {}
    composite = breakdown.get("composite_by_mode")
    if isinstance(composite, dict) and mode.value in composite:
        return float(composite[mode.value])
    return float(candidate.suitability_score or 0.0)


class CandidateService:
    def __init__(
        self,
        projects: ProjectService,
        requirements: RequirementProfileRepository,
        constraints: ConstraintProfileRepository,
        candidates: SolutionCandidateRepository,
        capability_registry: CapabilityRegistryReader,
        template_registry: ArchitectureTemplateRegistryReader,
        engine: CandidatePlanningEngine,
    ) -> None:
        self._projects = projects
        self._requirements = requirements
        self._constraints = constraints
        self._candidates = candidates
        self._capability_registry = capability_registry
        self._template_registry = template_registry
        self._engine = engine

    async def generate_candidates(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
        scoring_mode: ScoringMode,
    ) -> list[SolutionCandidate]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        rev = await self._requirements.get_by_id(requirement_id)
        if rev is None or rev.project_id != project_id:
            raise NotFoundError("Requirement not found", code="requirement_not_found")

        constraint = await self._constraints.get_for_requirement(requirement_id)
        templates = await self._template_registry.list_templates()
        capabilities = await self._capability_registry.list_capabilities()

        generated = await self._engine.synthesize_and_score(
            requirement=rev.profile,
            constraint=constraint,
            templates=templates,
            capabilities=capabilities,
            generation_mode=scoring_mode,
        )

        batch_id = uuid.uuid4()
        return await self._candidates.create_in_batch(
            project_id=project_id,
            requirement_profile_id=requirement_id,
            generation_batch_id=batch_id,
            candidates=generated,
        )

    async def list_candidates(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
        sort_mode: ScoringMode,
    ) -> list[SolutionCandidate]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        rev = await self._requirements.get_by_id(requirement_id)
        if rev is None or rev.project_id != project_id:
            raise NotFoundError("Requirement not found", code="requirement_not_found")
        return await self._candidates.list_latest_batch(
            requirement_profile_id=requirement_id,
            sort_mode=sort_mode,
        )

    async def generate_recommendations_for_project(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        scoring_mode: ScoringMode,
        requirement_id: UUID | None,
    ) -> list[SolutionCandidate]:
        target = await self._resolve_requirement_for_project(
            owner_user_id=owner_user_id,
            project_id=project_id,
            requirement_id=requirement_id,
        )
        return await self.generate_candidates(
            owner_user_id=owner_user_id,
            project_id=project_id,
            requirement_id=target,
            scoring_mode=scoring_mode,
        )

    async def list_recommendations_for_project(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        sort_mode: ScoringMode,
        requirement_id: UUID | None,
    ) -> list[SolutionCandidate]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        if requirement_id is not None:
            rev = await self._requirements.get_by_id(requirement_id)
            if rev is None or rev.project_id != project_id:
                raise NotFoundError("Requirement not found", code="requirement_not_found")
            return await self._candidates.list_latest_batch(
                requirement_profile_id=requirement_id,
                sort_mode=sort_mode,
            )

        revisions = await self._requirements.list_for_project(project_id)
        merged: list[SolutionCandidate] = []
        for rev in revisions:
            batch = await self._candidates.list_latest_batch(
                requirement_profile_id=rev.requirement_id,
                sort_mode=sort_mode,
            )
            merged.extend(batch)
        merged.sort(key=lambda c: _sort_key(c, sort_mode), reverse=True)
        return merged

    async def get_recommendation_option(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        candidate_id: UUID,
    ) -> SolutionCandidate:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        row = await self._candidates.get_by_id(project_id, candidate_id)
        if row is None:
            raise NotFoundError("Recommendation not found", code="recommendation_not_found")
        return row

    async def _resolve_requirement_for_project(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID | None,
    ) -> UUID:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        if requirement_id is not None:
            rev = await self._requirements.get_by_id(requirement_id)
            if rev is None or rev.project_id != project_id:
                raise NotFoundError("Requirement not found", code="requirement_not_found")
            return requirement_id
        latest = await self._requirements.get_latest_for_project(project_id)
        if latest is None:
            raise NotFoundError(
                "No requirements for this project; create one before generating recommendations",
                code="requirement_not_found",
            )
        return latest.requirement_id
