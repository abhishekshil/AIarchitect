from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import RuntimeBuildJobRepository
from solution_planning_api.domain import RuntimeBuildJob, RuntimeBuildJobStatus
from solution_planning_api.infrastructure.persistence.mappers import runtime_build_job_from_record
from solution_planning_api.infrastructure.persistence.orm_models import RuntimeBuildJobRecord


class SqlAlchemyRuntimeBuildJobRepository(RuntimeBuildJobRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_pending(
        self,
        *,
        project_id: UUID,
        requirement_id: UUID | None,
        solution_candidate_id: UUID | None,
    ) -> RuntimeBuildJob:
        row = RuntimeBuildJobRecord(
            id=uuid.uuid4(),
            project_id=project_id,
            requirement_profile_id=requirement_id,
            solution_candidate_id=solution_candidate_id,
            status=RuntimeBuildJobStatus.PENDING.value,
            stage="queued",
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return runtime_build_job_from_record(row)

    async def get(self, project_id: UUID, job_id: UUID) -> RuntimeBuildJob | None:
        stmt = select(RuntimeBuildJobRecord).where(
            RuntimeBuildJobRecord.id == job_id,
            RuntimeBuildJobRecord.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return runtime_build_job_from_record(row) if row else None

    async def get_by_id(self, job_id: UUID) -> RuntimeBuildJob | None:
        row = await self._session.get(RuntimeBuildJobRecord, job_id)
        return runtime_build_job_from_record(row) if row else None

    async def update(
        self,
        job_id: UUID,
        *,
        status: RuntimeBuildJobStatus | None = None,
        stage: str | None = None,
        error_detail: str | None = None,
        runtime_graph_id: UUID | None = None,
        runtime_graph_version: int | None = None,
    ) -> None:
        row = await self._session.get(RuntimeBuildJobRecord, job_id)
        if row is None:
            return
        if status is not None:
            row.status = status.value
        if stage is not None:
            row.stage = stage
        if error_detail is not None:
            row.error_detail = error_detail
        if runtime_graph_id is not None:
            row.runtime_graph_id = runtime_graph_id
        if runtime_graph_version is not None:
            row.runtime_graph_version = runtime_graph_version
        await self._session.flush()
