from __future__ import annotations

from uuid import UUID

from solution_planning_api.application.errors import ConflictError, NotFoundError
from solution_planning_api.application.ports.registries import (
    ArchitectureTemplateRegistryReader,
    CapabilityRegistryReader,
)
from solution_planning_api.application.ports.repositories import (
    ArchitectureSelectionRepository,
    ConstraintProfileRepository,
    OnboardingProgressRepository,
    RequirementProfileRepository,
    SolutionCandidateRepository,
    TaskGraphRepository,
)
from solution_planning_api.application.ports.task_graph_building import TaskGraphBuilder
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.domain import ArchitectureSelection, TaskGraph


class ArchitectureSelectionService:
    def __init__(
        self,
        projects: ProjectService,
        requirements: RequirementProfileRepository,
        constraints: ConstraintProfileRepository,
        candidates: SolutionCandidateRepository,
        selections: ArchitectureSelectionRepository,
        task_graphs: TaskGraphRepository,
        templates: ArchitectureTemplateRegistryReader,
        capabilities: CapabilityRegistryReader,
        builder: TaskGraphBuilder,
        onboarding_progress: OnboardingProgressRepository,
    ) -> None:
        self._projects = projects
        self._requirements = requirements
        self._constraints = constraints
        self._candidates = candidates
        self._selections = selections
        self._task_graphs = task_graphs
        self._templates = templates
        self._capabilities = capabilities
        self._builder = builder
        self._onboarding_progress = onboarding_progress

    async def select_and_build_task_graph(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
        candidate_id: UUID,
    ) -> tuple[ArchitectureSelection, TaskGraph]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        rev = await self._requirements.get_by_id(requirement_id)
        if rev is None or rev.project_id != project_id:
            raise NotFoundError("Requirement not found", code="requirement_not_found")

        cand = await self._candidates.get_by_id(project_id, candidate_id)
        if cand is None:
            raise NotFoundError("Candidate not found", code="candidate_not_found")
        if cand.requirement_id != requirement_id:
            raise ConflictError(
                "Candidate does not belong to this requirement",
                code="candidate_requirement_mismatch",
            )

        tpl_id = cand.architecture_template_ref
        if not tpl_id:
            raise ConflictError(
                "Candidate has no architecture template reference",
                code="candidate_missing_template",
            )
        template = await self._templates.get_template(tpl_id)
        if template is None:
            raise NotFoundError(
                "Architecture template not found in registry",
                code="template_not_found",
            )

        caps_by_id = {c.capability_id: c for c in await self._capabilities.list_capabilities()}
        constraint = await self._constraints.get_for_requirement(requirement_id)

        graph = self._builder.build(
            candidate=cand,
            requirement=rev.profile,
            constraint=constraint,
            template=template,
            capabilities_by_id=caps_by_id,
        )

        selection = await self._selections.replace_for_requirement(
            project_id=project_id,
            requirement_profile_id=requirement_id,
            solution_candidate_id=candidate_id,
        )
        stored = await self._task_graphs.upsert_for_candidate(
            project_id=project_id,
            solution_candidate_id=candidate_id,
            graph=graph,
        )
        await self._onboarding_progress.delete_for_requirement_except_graph(
            requirement_profile_id=requirement_id,
            keep_task_graph_id=stored.task_graph_id,
        )
        return selection, stored

    async def get_selection_with_task_graph(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
    ) -> tuple[ArchitectureSelection, TaskGraph]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        rev = await self._requirements.get_by_id(requirement_id)
        if rev is None or rev.project_id != project_id:
            raise NotFoundError("Requirement not found", code="requirement_not_found")

        sel = await self._selections.get_latest_for_requirement(requirement_id)
        if sel is None:
            raise NotFoundError("No architecture selection for this requirement", code="no_selection")

        tg = await self._task_graphs.get_for_candidate(project_id, sel.solution_candidate_id)
        if tg is None:
            raise NotFoundError(
                "Task graph not found for the selected candidate",
                code="task_graph_not_found",
            )
        return sel, tg
