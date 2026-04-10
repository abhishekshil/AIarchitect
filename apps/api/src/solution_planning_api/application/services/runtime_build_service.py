from __future__ import annotations

import asyncio
from datetime import datetime
from uuid import UUID

from solution_planning_api.application.errors import NotFoundError
from solution_planning_api.application.ports.registries import ArchitectureTemplateRegistryReader
from solution_planning_api.application.ports.repositories import (
    ArchitectureSelectionRepository,
    RequirementProfileRepository,
    RuntimeBuildJobRepository,
    RuntimeGraphRepository,
    SolutionCandidateRepository,
    TaskGraphRepository,
)
from solution_planning_api.application.ports.runtime_graph_building import RuntimeGraphBuilder
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.domain import (
    RuntimeBuildJob,
    RuntimeBuildJobStatus,
    RuntimeGraph,
)


class RuntimeBuildService:
    def __init__(
        self,
        projects: ProjectService,
        requirements: RequirementProfileRepository,
        selections: ArchitectureSelectionRepository,
        candidates: SolutionCandidateRepository,
        templates: ArchitectureTemplateRegistryReader,
        task_graphs: TaskGraphRepository,
        runtime_graphs: RuntimeGraphRepository,
        jobs: RuntimeBuildJobRepository,
        builder: RuntimeGraphBuilder,
    ) -> None:
        self._projects = projects
        self._requirements = requirements
        self._selections = selections
        self._candidates = candidates
        self._templates = templates
        self._task_graphs = task_graphs
        self._runtime_graphs = runtime_graphs
        self._jobs = jobs
        self._builder = builder

    async def enqueue_build(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        requirement_id: UUID,
    ) -> RuntimeBuildJob:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        rev = await self._requirements.get_by_id(requirement_id)
        if rev is None or rev.project_id != project_id:
            raise NotFoundError("Requirement not found", code="requirement_not_found")

        sel = await self._selections.get_latest_for_requirement(requirement_id)
        if sel is None:
            raise NotFoundError(
                "No architecture selection for this requirement",
                code="no_selection",
            )

        return await self._jobs.create_pending(
            project_id=project_id,
            requirement_id=requirement_id,
            solution_candidate_id=sel.solution_candidate_id,
        )

    async def get_job(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        job_id: UUID,
    ) -> RuntimeBuildJob:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        job = await self._jobs.get(project_id, job_id)
        if job is None:
            raise NotFoundError("Build job not found", code="runtime_build_job_not_found")
        return job

    async def list_runtime_graph_versions(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
    ) -> list[tuple[int, UUID, datetime]]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        return await self._runtime_graphs.list_version_summaries(project_id)

    async def get_runtime_graph_version(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        version: int,
    ) -> RuntimeGraph:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        g = await self._runtime_graphs.get_by_version(project_id, version)
        if g is None:
            raise NotFoundError("Runtime graph version not found", code="runtime_graph_not_found")
        return g

    async def execute_build(self, job_id: UUID) -> None:
        job = await self._jobs.get_by_id(job_id)
        if job is None or job.status != RuntimeBuildJobStatus.PENDING:
            return

        try:
            await self._jobs.update(job_id, status=RuntimeBuildJobStatus.RUNNING, stage="load_context")
            await asyncio.sleep(0)

            if job.requirement_id is None:
                raise NotFoundError("Job missing requirement scope", code="runtime_build_invalid_job")

            sel = await self._selections.get_latest_for_requirement(job.requirement_id)
            if sel is None:
                raise NotFoundError("Architecture selection was removed", code="no_selection")

            cand = await self._candidates.get_by_id(job.project_id, sel.solution_candidate_id)
            if cand is None:
                raise NotFoundError("Selected candidate not found", code="candidate_not_found")

            tpl_id = cand.architecture_template_ref
            if not tpl_id:
                raise NotFoundError("Candidate missing template reference", code="candidate_missing_template")

            template = await self._templates.get_template(tpl_id)
            if template is None:
                raise NotFoundError("Template not in registry", code="template_not_found")

            tg = await self._task_graphs.get_for_candidate(job.project_id, sel.solution_candidate_id)

            await self._jobs.update(job_id, stage="compile_graph")
            await asyncio.sleep(0)

            built = self._builder.build(
                requirement_id=job.requirement_id,
                template=template,
                candidate=cand,
                task_graph=tg,
            )

            await self._jobs.update(job_id, stage="persist")
            next_v = await self._runtime_graphs.next_version(job.project_id)
            stored = await self._runtime_graphs.create(
                project_id=job.project_id,
                solution_candidate_id=sel.solution_candidate_id,
                version=next_v,
                graph=built,
            )

            await self._jobs.update(
                job_id,
                status=RuntimeBuildJobStatus.SUCCEEDED,
                stage="done",
                runtime_graph_id=stored.runtime_graph_id,
                runtime_graph_version=stored.version,
            )
        except NotFoundError as e:
            await self._jobs.update(
                job_id,
                status=RuntimeBuildJobStatus.FAILED,
                stage="failed",
                error_detail=e.message[:4000],
            )
        except Exception as e:
            await self._jobs.update(
                job_id,
                status=RuntimeBuildJobStatus.FAILED,
                stage="failed",
                error_detail=str(e)[:4000],
            )
