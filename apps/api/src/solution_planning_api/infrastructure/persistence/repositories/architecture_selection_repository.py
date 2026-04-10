from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import ArchitectureSelectionRepository
from solution_planning_api.domain import ArchitectureSelection
from solution_planning_api.infrastructure.persistence.mappers import architecture_selection_from_record
from solution_planning_api.infrastructure.persistence.orm_models import ArchitectureSelectionRecord


class SqlAlchemyArchitectureSelectionRepository(ArchitectureSelectionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace_for_requirement(
        self,
        *,
        project_id: UUID,
        requirement_profile_id: UUID,
        solution_candidate_id: UUID,
    ) -> ArchitectureSelection:
        await self._session.execute(
            delete(ArchitectureSelectionRecord).where(
                ArchitectureSelectionRecord.requirement_profile_id == requirement_profile_id
            )
        )
        row = ArchitectureSelectionRecord(
            project_id=project_id,
            requirement_profile_id=requirement_profile_id,
            solution_candidate_id=solution_candidate_id,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return architecture_selection_from_record(row)

    async def get_latest_for_requirement(
        self, requirement_profile_id: UUID
    ) -> ArchitectureSelection | None:
        stmt = (
            select(ArchitectureSelectionRecord)
            .where(ArchitectureSelectionRecord.requirement_profile_id == requirement_profile_id)
            .order_by(ArchitectureSelectionRecord.selected_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        found = result.scalar_one_or_none()
        return architecture_selection_from_record(found) if found else None
