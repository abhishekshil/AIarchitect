from __future__ import annotations

from solution_planning_api.application.ports.registries import (
    ArchitectureTemplateRegistryReader,
    CapabilityRegistryReader,
)
from solution_planning_api.domain import ArchitectureTemplate, CapabilityBlock


class RegistryQueryService:
    """Read-through facade for registry HTTP handlers."""

    def __init__(
        self,
        capabilities: CapabilityRegistryReader,
        templates: ArchitectureTemplateRegistryReader,
    ) -> None:
        self._capabilities = capabilities
        self._templates = templates

    async def list_capabilities(self) -> list[CapabilityBlock]:
        return await self._capabilities.list_capabilities()

    async def get_capability(self, capability_id: str) -> CapabilityBlock | None:
        return await self._capabilities.get_capability(capability_id)

    async def list_templates(self) -> list[ArchitectureTemplate]:
        return await self._templates.list_templates()

    async def get_template(self, template_id: str) -> ArchitectureTemplate | None:
        return await self._templates.get_template(template_id)
