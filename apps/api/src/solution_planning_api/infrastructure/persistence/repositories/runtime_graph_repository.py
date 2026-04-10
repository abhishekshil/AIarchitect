from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import RuntimeGraphRepository
from solution_planning_api.domain import RuntimeGraph
from solution_planning_api.infrastructure.persistence.mappers import (
    runtime_graph_from_record,
    runtime_graph_to_json,
)
from solution_planning_api.infrastructure.persistence.orm_models import RuntimeGraphRecord


class SqlAlchemyRuntimeGraphRepository(RuntimeGraphRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def next_version(self, project_id: UUID) -> int:
        stmt = select(func.coalesce(func.max(RuntimeGraphRecord.version), 0)).where(
            RuntimeGraphRecord.project_id == project_id
        )
        result = await self._session.execute(stmt)
        current = int(result.scalar_one())
        return current + 1

    async def create(
        self,
        *,
        project_id: UUID,
        solution_candidate_id: UUID | None,
        version: int,
        graph: RuntimeGraph,
    ) -> RuntimeGraph:
        gid = graph.runtime_graph_id
        aligned = graph.model_copy(
            update={
                "runtime_graph_id": gid,
                "project_id": project_id,
                "candidate_id": solution_candidate_id,
                "version": version,
            }
        )
        self._session.add(
            RuntimeGraphRecord(
                id=gid,
                project_id=project_id,
                solution_candidate_id=solution_candidate_id,
                version=version,
                payload=runtime_graph_to_json(aligned),
            )
        )
        await self._session.flush()
        row = await self._session.get(RuntimeGraphRecord, gid)
        assert row is not None
        return runtime_graph_from_record(row)

    async def get_by_version(self, project_id: UUID, version: int) -> RuntimeGraph | None:
        stmt = select(RuntimeGraphRecord).where(
            RuntimeGraphRecord.project_id == project_id,
            RuntimeGraphRecord.version == version,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return runtime_graph_from_record(row) if row else None

    async def list_version_summaries(
        self, project_id: UUID
    ) -> list[tuple[int, UUID, datetime]]:
        stmt = (
            select(RuntimeGraphRecord.version, RuntimeGraphRecord.id, RuntimeGraphRecord.created_at)
            .where(RuntimeGraphRecord.project_id == project_id)
            .order_by(RuntimeGraphRecord.version.desc())
        )
        result = await self._session.execute(stmt)
        return [(int(v), rid, ts) for v, rid, ts in result.all()]
