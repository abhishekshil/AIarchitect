from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.registries import ArchitectureTemplateRegistryReader
from solution_planning_api.domain import ArchitectureTemplate
from solution_planning_api.infrastructure.persistence.mappers import (
    architecture_template_from_record,
    architecture_template_to_json,
)
from solution_planning_api.infrastructure.persistence.orm_models import ArchitectureTemplateRecord


class SqlAlchemyArchitectureTemplateRegistryRepository(ArchitectureTemplateRegistryReader):
    """DB-backed architecture template catalog."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_templates(self) -> list[ArchitectureTemplate]:
        stmt = select(ArchitectureTemplateRecord).order_by(ArchitectureTemplateRecord.key.asc())
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [architecture_template_from_record(r) for r in rows]

    async def get_template(self, template_id: str) -> ArchitectureTemplate | None:
        stmt = select(ArchitectureTemplateRecord).where(ArchitectureTemplateRecord.key == template_id)
        res = await self._session.execute(stmt)
        found = res.scalar_one_or_none()
        return architecture_template_from_record(found) if found else None

    async def upsert_template(self, model: ArchitectureTemplate) -> None:
        stmt = select(ArchitectureTemplateRecord).where(ArchitectureTemplateRecord.key == model.template_id)
        res = await self._session.execute(stmt)
        row = res.scalar_one_or_none()
        payload = architecture_template_to_json(model)
        if row is None:
            self._session.add(
                ArchitectureTemplateRecord(
                    key=model.template_id,
                    payload=payload,
                )
            )
        else:
            row.payload = payload
        await self._session.flush()
