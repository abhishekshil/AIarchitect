from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import ConstraintProfileRepository
from solution_planning_api.domain import ConstraintProfile
from solution_planning_api.infrastructure.persistence.mappers import (
    constraint_profile_from_record,
    constraint_profile_to_json,
)
from solution_planning_api.infrastructure.persistence.orm_models import ConstraintProfileRecord


class SqlAlchemyConstraintProfileRepository(ConstraintProfileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, *, project_id: UUID, requirement_profile_id: UUID, profile: ConstraintProfile
    ) -> ConstraintProfile:
        row = ConstraintProfileRecord(
            id=profile.constraint_id,
            project_id=project_id,
            requirement_profile_id=requirement_profile_id,
            profile=constraint_profile_to_json(profile),
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return constraint_profile_from_record(row)

    async def get_for_requirement(self, requirement_id: UUID) -> ConstraintProfile | None:
        stmt = select(ConstraintProfileRecord).where(
            ConstraintProfileRecord.requirement_profile_id == requirement_id
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return constraint_profile_from_record(row) if row else None
