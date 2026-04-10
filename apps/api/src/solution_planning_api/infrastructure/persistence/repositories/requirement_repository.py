from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.dto.requirement import RequirementRevision
from solution_planning_api.application.errors import ConflictError
from solution_planning_api.application.ports.repositories import RequirementProfileRepository
from solution_planning_api.domain import RequirementProfile
from solution_planning_api.infrastructure.persistence.mappers import (
    requirement_profile_from_record,
    requirement_profile_to_json,
)
from solution_planning_api.infrastructure.persistence.orm_models import RequirementProfileRecord
from solution_planning_api.infrastructure.persistence.orm_models import ProjectRecord


def _to_revision(row: RequirementProfileRecord) -> RequirementRevision:
    return RequirementRevision(
        requirement_id=row.id,
        project_id=row.project_id,
        version=row.version,
        created_at=row.created_at,
        profile=requirement_profile_from_record(row),
    )


class SqlAlchemyRequirementProfileRepository(RequirementProfileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def next_version(self, project_id: UUID) -> int:
        stmt = select(func.coalesce(func.max(RequirementProfileRecord.version), 0)).where(
            RequirementProfileRecord.project_id == project_id
        )
        result = await self._session.execute(stmt)
        current = int(result.scalar_one())
        return current + 1

    async def create(
        self, *, project_id: UUID, version: int, profile: RequirementProfile
    ) -> RequirementRevision:
        row = RequirementProfileRecord(
            id=profile.requirement_id,
            project_id=project_id,
            version=version,
            profile=requirement_profile_to_json(profile),
        )
        self._session.add(row)
        try:
            await self._session.flush()
        except IntegrityError as e:
            await self._session.rollback()
            raise ConflictError("Requirement version conflict", code="requirement_version_conflict") from e

        await self._session.refresh(row)
        return _to_revision(row)

    async def get_by_id(self, requirement_id: UUID) -> RequirementRevision | None:
        row = await self._session.get(RequirementProfileRecord, requirement_id)
        return _to_revision(row) if row else None

    async def get_latest_for_project(self, project_id: UUID) -> RequirementRevision | None:
        stmt = (
            select(RequirementProfileRecord)
            .where(RequirementProfileRecord.project_id == project_id)
            .order_by(RequirementProfileRecord.version.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return _to_revision(row) if row else None

    async def list_for_project(
        self, project_id: UUID, *, owner_user_id: UUID | None = None
    ) -> list[RequirementRevision]:
        stmt = select(RequirementProfileRecord).where(
            RequirementProfileRecord.project_id == project_id
        )
        if owner_user_id is not None:
            stmt = stmt.join(
                ProjectRecord, RequirementProfileRecord.project_id == ProjectRecord.id
            ).where(ProjectRecord.owner_user_id == owner_user_id)
        stmt = stmt.order_by(RequirementProfileRecord.version.desc())
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [_to_revision(r) for r in rows]

    async def delete_by_id(self, requirement_id: UUID) -> bool:
        stmt = delete(RequirementProfileRecord).where(RequirementProfileRecord.id == requirement_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return (result.rowcount or 0) > 0
