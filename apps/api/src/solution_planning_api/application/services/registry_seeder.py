"""Load bundled YAML into PostgreSQL (idempotent upsert per key)."""

from __future__ import annotations

from importlib import resources

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.infrastructure.persistence.orm_models import (
    ArchitectureTemplateRecord,
    CapabilityBlockRecord,
)
from solution_planning_api.infrastructure.persistence.repositories.architecture_template_registry_repository import (
    SqlAlchemyArchitectureTemplateRegistryRepository,
)
from solution_planning_api.infrastructure.persistence.repositories.capability_registry_repository import (
    SqlAlchemyCapabilityRegistryRepository,
)
from solution_planning_api.infrastructure.registry import (
    parse_architecture_templates_yaml,
    parse_capabilities_yaml,
)


def _read_bundled(name: str) -> str:
    root = resources.files("solution_planning_api.registry_data")
    return (root / name).read_text(encoding="utf-8")


class RegistrySeeder:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._capabilities = SqlAlchemyCapabilityRegistryRepository(session)
        self._templates = SqlAlchemyArchitectureTemplateRegistryRepository(session)

    async def seed_all(self) -> tuple[int, int]:
        caps = parse_capabilities_yaml(_read_bundled("capabilities.yaml"))
        tpls = parse_architecture_templates_yaml(_read_bundled("architecture_templates.yaml"))
        for c in caps:
            await self._capabilities.upsert_capability(c, is_system=True)
        for t in tpls:
            await self._templates.upsert_template(t)
        return len(caps), len(tpls)


async def ensure_registries_seeded(session: AsyncSession) -> tuple[int, int] | None:
    """If either table is empty, load bundled YAML. Returns counts when seed ran, else None."""
    cap_count = await session.scalar(select(func.count()).select_from(CapabilityBlockRecord))
    tpl_count = await session.scalar(select(func.count()).select_from(ArchitectureTemplateRecord))
    if (cap_count or 0) > 0 and (tpl_count or 0) > 0:
        return None
    seeder = RegistrySeeder(session)
    return await seeder.seed_all()
