from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.repositories import ProjectRepository
from solution_planning_api.application.unset import UNSET, UnsetType
from solution_planning_api.domain import Project
from solution_planning_api.infrastructure.persistence.mappers import project_from_record
from solution_planning_api.infrastructure.persistence.orm_models import ProjectRecord


class SqlAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, *, owner_user_id: UUID, name: str, description: str | None
    ) -> Project:
        row = ProjectRecord(
            owner_user_id=owner_user_id,
            name=name.strip(),
            description=description.strip() if description is not None else None,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return project_from_record(row)

    async def get_by_id(self, project_id: UUID) -> Project | None:
        row = await self._session.get(ProjectRecord, project_id)
        return project_from_record(row) if row else None

    async def list_for_user(self, user_id: UUID) -> list[Project]:
        stmt = (
            select(ProjectRecord)
            .where(ProjectRecord.owner_user_id == user_id)
            .order_by(ProjectRecord.created_at.desc())
        )
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [project_from_record(r) for r in rows]

    async def update(
        self,
        *,
        project_id: UUID,
        owner_user_id: UUID,
        name: str | None | UnsetType,
        description: str | None | UnsetType,
    ) -> Project | None:
        row = await self._session.get(ProjectRecord, project_id)
        if row is None or row.owner_user_id != owner_user_id:
            return None

        if name is not UNSET:
            assert isinstance(name, str)
            row.name = name.strip()
        if description is not UNSET:
            if description is None:
                row.description = None
            else:
                row.description = description.strip() or None
        row.updated_at = datetime.now(UTC)
        await self._session.flush()
        await self._session.refresh(row)
        return project_from_record(row)

    async def delete(self, *, project_id: UUID, owner_user_id: UUID) -> bool:
        row = await self._session.get(ProjectRecord, project_id)
        if row is None or row.owner_user_id != owner_user_id:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True
