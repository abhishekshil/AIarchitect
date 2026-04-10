from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import PlaygroundInferenceRepository
from solution_planning_api.domain import PlaygroundInferenceRun
from solution_planning_api.infrastructure.persistence.mappers import playground_inference_summary_from_record
from solution_planning_api.infrastructure.persistence.orm_models import PlaygroundInferenceRunRecord


class SqlAlchemyPlaygroundInferenceRepository(PlaygroundInferenceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

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
    ) -> PlaygroundInferenceRun:
        row = PlaygroundInferenceRunRecord(
            id=inference_id,
            project_id=project_id,
            runtime_graph_id=runtime_graph_id,
            runtime_graph_version=runtime_graph_version,
            architecture_pattern=architecture_pattern,
            input_text=input_text,
            request_payload=request_payload,
            response_payload=response_payload,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return playground_inference_summary_from_record(row)

    async def list_runs(self, project_id: UUID, *, limit: int = 50) -> list[PlaygroundInferenceRun]:
        stmt = (
            select(PlaygroundInferenceRunRecord)
            .where(PlaygroundInferenceRunRecord.project_id == project_id)
            .order_by(desc(PlaygroundInferenceRunRecord.created_at))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [playground_inference_summary_from_record(r) for r in rows]

    async def get_response_payload(
        self, project_id: UUID, inference_id: UUID
    ) -> dict[str, Any] | None:
        stmt = select(PlaygroundInferenceRunRecord).where(
            PlaygroundInferenceRunRecord.id == inference_id,
            PlaygroundInferenceRunRecord.project_id == project_id,
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return dict(row.response_payload) if row else None
