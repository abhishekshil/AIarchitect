"""
Read-only registry ports for capabilities and architecture templates.

Implementations load from the database (seeded from YAML/JSON under `registry_data/`).
TODO: Add admin write APIs or external config sync without changing these read contracts.
"""

from __future__ import annotations

from typing import Protocol

from solution_planning_api.domain import ArchitectureTemplate, CapabilityBlock


class CapabilityRegistryReader(Protocol):
    async def list_capabilities(self) -> list[CapabilityBlock]: ...
    async def get_capability(self, capability_id: str) -> CapabilityBlock | None: ...


class ArchitectureTemplateRegistryReader(Protocol):
    async def list_templates(self) -> list[ArchitectureTemplate]: ...
    async def get_template(self, template_id: str) -> ArchitectureTemplate | None: ...
