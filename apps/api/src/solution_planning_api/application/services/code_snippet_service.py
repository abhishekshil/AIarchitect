from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from solution_planning_api.application.errors import NotFoundError
from solution_planning_api.application.dto.code_snippets import SnippetGenerationContext
from solution_planning_api.application.ports.repositories import CodeSnippetBundleRepository, RuntimeGraphRepository
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.domain import CodeSnippetBundleSummary
from solution_planning_api.domain.architecture_pattern import infer_architecture_pattern_from_runtime_graph
from solution_planning_api.infrastructure.snippets import assemble_snippet_bundle_payload


class CodeSnippetService:
    def __init__(
        self,
        projects: ProjectService,
        runtime_graphs: RuntimeGraphRepository,
        bundles: CodeSnippetBundleRepository,
        *,
        snippet_base_url: str,
    ) -> None:
        self._projects = projects
        self._runtime_graphs = runtime_graphs
        self._bundles = bundles
        self._snippet_base_url = snippet_base_url.rstrip("/")

    async def generate_and_persist(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        runtime_graph_version: int | None,
    ) -> dict[str, Any]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        version = runtime_graph_version
        if version is None:
            summaries = await self._runtime_graphs.list_version_summaries(project_id)
            if not summaries:
                raise NotFoundError(
                    "No runtime graph for this project; run a runtime build first.",
                    code="no_runtime_graph",
                )
            version, _, _ = summaries[0]

        graph = await self._runtime_graphs.get_by_version(project_id, version)
        if graph is None:
            raise NotFoundError("Runtime graph version not found", code="runtime_graph_not_found")

        pattern = infer_architecture_pattern_from_runtime_graph(graph)
        pb = graph.provider_bindings or {}
        ctx = SnippetGenerationContext(
            base_url=self._snippet_base_url,
            project_id=project_id,
            runtime_graph_id=graph.runtime_graph_id,
            runtime_graph_version=graph.version,
            architecture_pattern=pattern,
            architecture_template_id=pb.get("architecture_template_id"),
        )
        bundle_id = uuid.uuid4()
        payload = assemble_snippet_bundle_payload(bundle_id=bundle_id, ctx=ctx)
        await self._bundles.create_bundle(
            bundle_id=bundle_id,
            project_id=project_id,
            runtime_graph_id=graph.runtime_graph_id,
            runtime_graph_version=graph.version,
            architecture_pattern=pattern,
            payload=payload,
        )
        return payload

    async def list_bundles(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        limit: int = 20,
    ) -> list[CodeSnippetBundleSummary]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        return await self._bundles.list_bundles(project_id, limit=limit)

    async def get_bundle_payload(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        bundle_id: UUID,
    ) -> dict[str, Any]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        payload = await self._bundles.get_payload(project_id, bundle_id)
        if payload is None:
            raise NotFoundError("Snippet bundle not found", code="snippet_bundle_not_found")
        return payload
