from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import TaskGraphRepository
from solution_planning_api.domain import TaskGraph
from solution_planning_api.infrastructure.persistence.mappers import (
    task_graph_from_record,
    task_graph_to_json,
)
from solution_planning_api.infrastructure.persistence.orm_models import TaskGraphRecord


class SqlAlchemyTaskGraphRepository(TaskGraphRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_for_candidate(
        self,
        *,
        project_id: UUID,
        solution_candidate_id: UUID,
        graph: TaskGraph,
    ) -> TaskGraph:
        stmt = select(TaskGraphRecord).where(
            TaskGraphRecord.solution_candidate_id == solution_candidate_id
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            payload = task_graph_to_json(graph)
            self._session.add(
                TaskGraphRecord(
                    id=graph.task_graph_id,
                    project_id=project_id,
                    solution_candidate_id=solution_candidate_id,
                    payload=payload,
                )
            )
        else:
            aligned = graph.model_copy(update={"task_graph_id": row.id})
            row.project_id = project_id
            row.payload = task_graph_to_json(aligned)
        await self._session.flush()
        res = await self._session.execute(
            select(TaskGraphRecord).where(
                TaskGraphRecord.solution_candidate_id == solution_candidate_id
            )
        )
        final = res.scalar_one()
        return task_graph_from_record(final)

    async def get_for_candidate(
        self, project_id: UUID, solution_candidate_id: UUID
    ) -> TaskGraph | None:
        stmt = select(TaskGraphRecord).where(
            TaskGraphRecord.project_id == project_id,
            TaskGraphRecord.solution_candidate_id == solution_candidate_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return task_graph_from_record(row) if row else None
