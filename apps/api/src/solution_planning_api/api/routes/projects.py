from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from solution_planning_api.api.deps import CurrentUser, get_project_service
from solution_planning_api.api.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.application.unset import UNSET

router = APIRouter()


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    current: CurrentUser,
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> list[ProjectResponse]:
    rows = await projects.list_projects(current.user_id)
    return [ProjectResponse.from_domain(p) for p in rows]


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    body: ProjectCreate,
    current: CurrentUser,
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    created = await projects.create_project(
        owner_user_id=current.user_id,
        name=body.name,
        description=body.description,
    )
    return ProjectResponse.from_domain(created)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current: CurrentUser,
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    project = await projects.get_project(owner_user_id=current.user_id, project_id=project_id)
    return ProjectResponse.from_domain(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    body: ProjectUpdate,
    current: CurrentUser,
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> ProjectResponse:
    name_u = body.name if "name" in body.model_fields_set else UNSET
    desc_u = body.description if "description" in body.model_fields_set else UNSET
    updated = await projects.update_project(
        owner_user_id=current.user_id,
        project_id=project_id,
        name=name_u,
        description=desc_u,
    )
    return ProjectResponse.from_domain(updated)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current: CurrentUser,
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> None:
    await projects.delete_project(owner_user_id=current.user_id, project_id=project_id)
