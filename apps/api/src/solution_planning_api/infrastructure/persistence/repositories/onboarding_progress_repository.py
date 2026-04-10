from __future__ import annotations

import uuid
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import OnboardingProgressRepository
from solution_planning_api.domain.onboarding import OnboardingTaskProgress, OnboardingTaskState
from solution_planning_api.infrastructure.persistence.mappers import onboarding_progress_from_record
from solution_planning_api.infrastructure.persistence.orm_models import OnboardingTaskProgressRecord


class SqlAlchemyOnboardingProgressRepository(OnboardingProgressRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_task_graph(self, task_graph_id: UUID) -> list[OnboardingTaskProgress]:
        stmt = select(OnboardingTaskProgressRecord).where(
            OnboardingTaskProgressRecord.task_graph_id == task_graph_id
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [onboarding_progress_from_record(r) for r in rows]

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
    ) -> OnboardingTaskProgress:
        row_id = uuid.uuid4()
        insert_stmt = pg_insert(OnboardingTaskProgressRecord).values(
            id=row_id,
            project_id=project_id,
            requirement_profile_id=requirement_profile_id,
            task_graph_id=task_graph_id,
            node_id=node_id,
            state=state.value,
            response=response,
            validation_feedback=validation_feedback,
        )
        upsert_stmt = insert_stmt.on_conflict_do_update(
            constraint="uq_onboarding_progress_graph_node",
            set_={
                "state": state.value,
                "response": response,
                "validation_feedback": validation_feedback,
                "updated_at": func.now(),
            },
        ).returning(OnboardingTaskProgressRecord)
        result = await self._session.execute(upsert_stmt)
        saved = result.scalar_one()
        return onboarding_progress_from_record(saved)

    async def delete_for_requirement_except_graph(
        self, requirement_profile_id: UUID, keep_task_graph_id: UUID
    ) -> None:
        await self._session.execute(
            delete(OnboardingTaskProgressRecord).where(
                OnboardingTaskProgressRecord.requirement_profile_id == requirement_profile_id,
                OnboardingTaskProgressRecord.task_graph_id != keep_task_graph_id,
            )
        )
