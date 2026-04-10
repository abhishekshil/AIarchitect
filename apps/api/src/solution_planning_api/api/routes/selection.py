from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from solution_planning_api.api.deps import CurrentUser, get_architecture_selection_service
from solution_planning_api.api.schemas.selection import (
    ArchitectureSelectionEnvelope,
    SelectArchitectureRequest,
)
from solution_planning_api.application.services.architecture_selection_service import (
    ArchitectureSelectionService,
)

router = APIRouter(
    prefix="/{project_id}/requirements/{requirement_id}/architecture-selection",
    tags=["architecture-selection"],
)


@router.post(
    "/",
    response_model=ArchitectureSelectionEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def select_architecture(
    project_id: UUID,
    requirement_id: UUID,
    body: SelectArchitectureRequest,
    current: CurrentUser,
    svc: Annotated[ArchitectureSelectionService, Depends(get_architecture_selection_service)],
) -> ArchitectureSelectionEnvelope:
    """Persist the chosen candidate and generate the onboarding task graph."""
    selection, task_graph = await svc.select_and_build_task_graph(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
        candidate_id=body.candidate_id,
    )
    return ArchitectureSelectionEnvelope(selection=selection, task_graph=task_graph)


@router.get("/", response_model=ArchitectureSelectionEnvelope)
async def get_architecture_selection(
    project_id: UUID,
    requirement_id: UUID,
    current: CurrentUser,
    svc: Annotated[ArchitectureSelectionService, Depends(get_architecture_selection_service)],
) -> ArchitectureSelectionEnvelope:
    """Return the current selection and its persisted task graph."""
    selection, task_graph = await svc.get_selection_with_task_graph(
        owner_user_id=current.user_id,
        project_id=project_id,
        requirement_id=requirement_id,
    )
    return ArchitectureSelectionEnvelope(selection=selection, task_graph=task_graph)
