from __future__ import annotations

import uuid
from typing import Any
from uuid import UUID

from solution_planning_api.application.errors import NotFoundError
from solution_planning_api.application.ports.inference_simulation import PlaygroundInferenceSimulator
from solution_planning_api.application.ports.repositories import (
    PlaygroundInferenceRepository,
    RuntimeGraphRepository,
)
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.domain import PlaygroundInferenceRun


class InferencePlaygroundService:
    def __init__(
        self,
        projects: ProjectService,
        runtime_graphs: RuntimeGraphRepository,
        history: PlaygroundInferenceRepository,
        simulator: PlaygroundInferenceSimulator,
    ) -> None:
        self._projects = projects
        self._runtime_graphs = runtime_graphs
        self._history = history
        self._simulator = simulator

    async def run_infer(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        runtime_graph_version: int,
        input_text: str,
    ) -> dict[str, Any]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        graph = await self._runtime_graphs.get_by_version(project_id, runtime_graph_version)
        if graph is None:
            raise NotFoundError("Runtime graph version not found", code="runtime_graph_not_found")

        sim = self._simulator.run(graph=graph, input_text=input_text)
        inference_id = uuid.uuid4()
        request_payload = {
            "runtime_graph_version": runtime_graph_version,
            "input_text": input_text,
        }
        response_payload: dict[str, Any] = {
            "schema_version": "1.0",
            "inference_id": str(inference_id),
            "runtime_graph_id": str(graph.runtime_graph_id),
            "runtime_graph_version": graph.version,
            **sim,
        }

        await self._history.create_run(
            inference_id=inference_id,
            project_id=project_id,
            runtime_graph_id=graph.runtime_graph_id,
            runtime_graph_version=graph.version,
            architecture_pattern=sim["architecture_pattern"],
            input_text=input_text,
            request_payload=request_payload,
            response_payload=_json_safe(response_payload),
        )

        response_payload["inference_id"] = inference_id
        response_payload["runtime_graph_id"] = graph.runtime_graph_id
        return response_payload

    async def list_history(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        limit: int = 50,
    ) -> list[PlaygroundInferenceRun]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        return await self._history.list_runs(project_id, limit=limit)

    async def get_inference_detail(
        self,
        *,
        owner_user_id: UUID,
        project_id: UUID,
        inference_id: UUID,
    ) -> dict[str, Any]:
        await self._projects.get_project(owner_user_id=owner_user_id, project_id=project_id)
        payload = await self._history.get_response_payload(project_id, inference_id)
        if payload is None:
            raise NotFoundError("Inference run not found", code="inference_not_found")
        return payload


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(x) for x in obj]
    return obj
