from __future__ import annotations

from typing import Any
from uuid import UUID

from solution_planning_api.application.errors import ConflictError, NotFoundError
from solution_planning_api.application.ports.repositories import (
    ArchitectureSelectionRepository,
    OnboardingProgressRepository,
    RequirementProfileRepository,
    TaskGraphRepository,
)
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.application.onboarding.response_validate import (
    feedback_object,
    validate_onboarding_response,
)
from solution_planning_api.application.onboarding.llm_guidance import LLMOnboardingGuidance
from solution_planning_api.application.onboarding.ui_hints import ui_hints_for_node
from solution_planning_api.domain import OnboardingTaskProgress, OnboardingTaskState, TaskGraph, TaskGraphNode
from solution_planning_api.domain.common import JsonObject


class OnboardingService:
    def __init__(
        self,
        projects: ProjectService,
        requirements: RequirementProfileRepository,
        selections: ArchitectureSelectionRepository,
        task_graphs: TaskGraphRepository,
        progress: OnboardingProgressRepository,
        guidance: LLMOnboardingGuidance | None = None,
    ) -> None:
        self._projects = projects
        self._requirements = requirements
        self._selections = selections
        self._task_graphs = task_graphs
        self._progress = progress
        self._guidance = guidance or LLMOnboardingGuidance(None)

    async def list_tasks(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
    ) -> tuple[TaskGraph, list[dict[str, Any]]]:
        tg, by_node, _, _ = await self._load_context(
            owner_user_id=owner_user_id,
            project_id=project_id,
            requirement_id=requirement_id,
        )
        items = [await self._task_to_item(n, by_node.get(n.node_id)) for n in tg.nodes]
        return tg, items

    async def get_task(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
        node_id: str,
    ) -> dict[str, Any]:
        tg, by_node, _, _ = await self._load_context(
            owner_user_id=owner_user_id,
            project_id=project_id,
            requirement_id=requirement_id,
        )
        node = _find_node(tg, node_id)
        return await self._task_to_item(node, by_node.get(node_id))

    async def start_task(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
        node_id: str,
    ) -> dict[str, Any]:
        tg, by_node, pid, rid = await self._load_context(
            owner_user_id=owner_user_id,
            project_id=project_id,
            requirement_id=requirement_id,
        )
        node = _find_node(tg, node_id)
        cur = by_node.get(node_id)
        st = cur.state if cur else OnboardingTaskState.NOT_STARTED
        if st == OnboardingTaskState.COMPLETED:
            raise ConflictError("Task is already completed", code="task_already_completed")
        if st == OnboardingTaskState.IN_PROGRESS:
            return await self._task_to_item(node, cur)
        saved = await self._progress.upsert(
            project_id=pid,
            requirement_profile_id=rid,
            task_graph_id=tg.task_graph_id,
            node_id=node_id,
            state=OnboardingTaskState.IN_PROGRESS,
            response=cur.response if cur else None,
            validation_feedback=cur.validation_feedback if cur else None,
        )
        return await self._task_to_item(node, saved)

    async def submit_task(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
        node_id: str,
        response: JsonObject,
    ) -> dict[str, Any]:
        tg, by_node, pid, rid = await self._load_context(
            owner_user_id=owner_user_id,
            project_id=project_id,
            requirement_id=requirement_id,
        )
        node = _find_node(tg, node_id)
        cur = by_node.get(node_id)
        st = cur.state if cur else OnboardingTaskState.NOT_STARTED
        if st == OnboardingTaskState.COMPLETED:
            raise ConflictError("Task is already completed", code="task_already_completed")

        errors, warnings = validate_onboarding_response(
            task_type=node.task_type,
            response=response,
        )
        if errors:
            fb = feedback_object(errors=errors, warnings=warnings, status="rejected")
            saved = await self._progress.upsert(
                project_id=pid,
                requirement_profile_id=rid,
                task_graph_id=tg.task_graph_id,
                node_id=node_id,
                state=OnboardingTaskState.REQUIRES_REVISION,
                response=dict(response),
                validation_feedback=fb,
            )
            return await self._task_to_item(node, saved)

        fb = feedback_object(errors=[], warnings=warnings, status="accepted")
        await self._progress.upsert(
            project_id=pid,
            requirement_profile_id=rid,
            task_graph_id=tg.task_graph_id,
            node_id=node_id,
            state=OnboardingTaskState.SUBMITTED,
            response=dict(response),
            validation_feedback=fb,
        )
        fb_done = {
            **feedback_object(errors=[], warnings=warnings, status="validated"),
            "pipeline": ["submitted", "validated", "completed"],
        }
        saved = await self._progress.upsert(
            project_id=pid,
            requirement_profile_id=rid,
            task_graph_id=tg.task_graph_id,
            node_id=node_id,
            state=OnboardingTaskState.COMPLETED,
            response=dict(response),
            validation_feedback=fb_done,
        )
        return await self._task_to_item(node, saved)

    async def progress_snapshot(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
    ) -> dict[str, Any]:
        tg, by_node, _, _ = await self._load_context(
            owner_user_id=owner_user_id,
            project_id=project_id,
            requirement_id=requirement_id,
        )
        total = len(tg.nodes)
        by_state: dict[str, int] = {s.value: 0 for s in OnboardingTaskState}
        completed = 0
        for n in tg.nodes:
            p = by_node.get(n.node_id)
            st = p.state.value if p else OnboardingTaskState.NOT_STARTED.value
            by_state[st] += 1
            if st == OnboardingTaskState.COMPLETED.value:
                completed += 1
        pct = round(100.0 * completed / total, 2) if total else 0.0
        return {
            "schema_version": "1.0",
            "task_graph_id": tg.task_graph_id,
            "total_tasks": total,
            "by_state": by_state,
            "percent_completed": pct,
        }

    async def _load_context(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
    ) -> tuple[TaskGraph, dict[str, OnboardingTaskProgress], UUID, UUID]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        rev = await self._requirements.get_by_id(requirement_id)
        if rev is None or rev.project_id != project_id:
            raise NotFoundError("Requirement not found", code="requirement_not_found")

        sel = await self._selections.get_latest_for_requirement(requirement_id)
        if sel is None:
            raise NotFoundError(
                "No architecture selection for this requirement; select an architecture first",
                code="no_selection",
            )
        tg = await self._task_graphs.get_for_candidate(project_id, sel.solution_candidate_id)
        if tg is None:
            raise NotFoundError(
                "Task graph not found for the selected candidate",
                code="task_graph_not_found",
            )
        rows = await self._progress.list_for_task_graph(tg.task_graph_id)
        by_node = {r.node_id: r for r in rows}
        return tg, by_node, project_id, requirement_id

    async def _task_to_item(
        self,
        node: TaskGraphNode,
        progress: OnboardingTaskProgress | None,
    ) -> dict[str, Any]:
        suggestions, placeholder = ui_hints_for_node(node)
        suggestions, placeholder = await self._guidance.enrich(
            node=node,
            suggestions=suggestions,
            placeholder=placeholder,
        )
        state = progress.state if progress else OnboardingTaskState.NOT_STARTED
        return {
            "node_id": node.node_id,
            "title": node.title,
            "description": node.description,
            "task_type": node.task_type,
            "metadata": node.metadata,
            "guidance_refs": list(node.guidance_refs),
            "condition": node.condition,
            "state": state.value,
            "suggestions": suggestions,
            "example_placeholder": placeholder,
            "response": dict(progress.response) if progress and progress.response else None,
            "validation_feedback": dict(progress.validation_feedback)
            if progress and progress.validation_feedback
            else None,
            "updated_at": progress.updated_at.isoformat() if progress and progress.updated_at else None,
        }


def _find_node(tg: TaskGraph, node_id: str) -> TaskGraphNode:
    for n in tg.nodes:
        if n.node_id == node_id:
            return n
    raise NotFoundError("Onboarding task not found in graph", code="onboarding_task_not_found")
