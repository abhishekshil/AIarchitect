from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.ports.registries import CapabilityRegistryReader
from solution_planning_api.domain import CapabilityBlock
from solution_planning_api.infrastructure.persistence.mappers import (
    capability_block_from_record,
    capability_block_to_json,
)
from solution_planning_api.infrastructure.persistence.orm_models import CapabilityBlockRecord


class SqlAlchemyCapabilityRegistryRepository(CapabilityRegistryReader):
    """DB-backed capability catalog (rows seeded from YAML)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_capabilities(self) -> list[CapabilityBlock]:
        stmt = select(CapabilityBlockRecord).order_by(CapabilityBlockRecord.key.asc())
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [capability_block_from_record(r) for r in rows]

    async def get_capability(self, capability_id: str) -> CapabilityBlock | None:
        stmt = select(CapabilityBlockRecord).where(CapabilityBlockRecord.key == capability_id)
        res = await self._session.execute(stmt)
        found = res.scalar_one_or_none()
        return capability_block_from_record(found) if found else None

    async def upsert_capability(self, model: CapabilityBlock, *, is_system: bool = True) -> None:
        stmt = select(CapabilityBlockRecord).where(CapabilityBlockRecord.key == model.capability_id)
        res = await self._session.execute(stmt)
        row = res.scalar_one_or_none()
        payload = capability_block_to_json(model)
        if row is None:
            self._session.add(
                CapabilityBlockRecord(
                    key=model.capability_id,
                    payload=payload,
                    is_system=is_system,
                )
            )
        else:
            row.payload = payload
            row.is_system = is_system
        await self._session.flush()
