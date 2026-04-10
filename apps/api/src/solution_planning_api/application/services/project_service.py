from __future__ import annotations

from uuid import UUID

from solution_planning_api.application.errors import ForbiddenError, NotFoundError
from solution_planning_api.application.ports.repositories import ProjectRepository
from solution_planning_api.application.unset import UNSET, UnsetType
from solution_planning_api.domain import Project


class ProjectService:
    def __init__(self, projects: ProjectRepository) -> None:
        self._projects = projects

    async def list_projects(self, owner_user_id: UUID) -> list[Project]:
        return await self._projects.list_for_user(owner_user_id)

    async def get_project(self, *, owner_user_id: UUID, project_id: UUID) -> Project:
        project = await self._projects.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project not found", code="project_not_found")
        if project.owner_user_id != owner_user_id:
            raise ForbiddenError("Not allowed to access this project")
        return project

    async def create_project(
        self, *, owner_user_id: UUID, name: str, description: str | None
    ) -> Project:
        return await self._projects.create(
            owner_user_id=owner_user_id, name=name, description=description
        )

    async def update_project(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        name: str | None | UnsetType = UNSET,
        description: str | None | UnsetType = UNSET,
    ) -> Project:
        await self.get_project(owner_user_id=owner_user_id, project_id=project_id)
        if name is UNSET and description is UNSET:
            existing = await self._projects.get_by_id(project_id)
            assert existing is not None
            return existing

        updated = await self._projects.update(
            project_id=project_id,
            owner_user_id=owner_user_id,
            name=name,
            description=description,
        )
        if updated is None:
            raise NotFoundError("Project not found", code="project_not_found")
        return updated

    async def delete_project(self, *, owner_user_id: UUID, project_id: UUID) -> None:
        await self.get_project(owner_user_id=owner_user_id, project_id=project_id)
        deleted = await self._projects.delete(project_id=project_id, owner_user_id=owner_user_id)
        if not deleted:
            raise NotFoundError("Project not found", code="project_not_found")
