from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from solution_planning_api.api.deps import CurrentUser, get_registry_query_service
from solution_planning_api.application.errors import NotFoundError
from solution_planning_api.application.services.registry_query_service import RegistryQueryService
from solution_planning_api.domain import ArchitectureTemplate, CapabilityBlock

router = APIRouter(prefix="/registry", tags=["registry"])


@router.get("/capabilities", response_model=list[CapabilityBlock])
async def list_capabilities(
    _current: CurrentUser,
    svc: Annotated[RegistryQueryService, Depends(get_registry_query_service)],
) -> list[CapabilityBlock]:
    return await svc.list_capabilities()


@router.get("/capabilities/{capability_id}", response_model=CapabilityBlock)
async def get_capability(
    capability_id: str,
    _current: CurrentUser,
    svc: Annotated[RegistryQueryService, Depends(get_registry_query_service)],
) -> CapabilityBlock:
    item = await svc.get_capability(capability_id)
    if item is None:
        raise NotFoundError("Capability not found", code="capability_not_found")
    return item


@router.get("/architecture-templates", response_model=list[ArchitectureTemplate])
async def list_architecture_templates(
    _current: CurrentUser,
    svc: Annotated[RegistryQueryService, Depends(get_registry_query_service)],
) -> list[ArchitectureTemplate]:
    return await svc.list_templates()


@router.get("/architecture-templates/{template_id}", response_model=ArchitectureTemplate)
async def get_architecture_template(
    template_id: str,
    _current: CurrentUser,
    svc: Annotated[RegistryQueryService, Depends(get_registry_query_service)],
) -> ArchitectureTemplate:
    item = await svc.get_template(template_id)
    if item is None:
        raise NotFoundError("Architecture template not found", code="template_not_found")
    return item
