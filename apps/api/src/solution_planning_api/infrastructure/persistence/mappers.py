"""
Translate between ORM rows and Pydantic domain models.

Row-level columns (ids, FKs) are authoritative; JSON payloads may omit or mirror them.
"""

from __future__ import annotations

from typing import Any

from solution_planning_api.domain import (
    ArchitectureSelection,
    ArchitectureTemplate,
    CapabilityBlock,
    CodeSnippetBundleSummary,
    ConstraintProfile,
    EvaluationPlan,
    IntegrationPackage,
    PlaygroundInferenceRun,
    Project,
    RequirementProfile,
    RuntimeBuildJob,
    RuntimeBuildJobStatus,
    RuntimeGraph,
    SolutionCandidate,
    TaskGraph,
    User,
)
from solution_planning_api.domain.onboarding import OnboardingTaskProgress, OnboardingTaskState
from solution_planning_api.infrastructure.persistence.orm_models import (
    ArchitectureSelectionRecord,
    ArchitectureTemplateRecord,
    CapabilityBlockRecord,
    CodeSnippetBundleRecord,
    ConstraintProfileRecord,
    EvaluationPlanRecord,
    IntegrationPackageRecord,
    ProjectRecord,
    RequirementProfileRecord,
    RuntimeBuildJobRecord,
    RuntimeGraphRecord,
    SolutionCandidateRecord,
    OnboardingTaskProgressRecord,
    PlaygroundInferenceRunRecord,
    TaskGraphRecord,
    UserRecord,
)


def user_from_record(row: UserRecord) -> User:
    return User(
        user_id=row.id,
        email=row.email,
        password_hash=row.password_hash,
        created_at=row.created_at,
    )


def project_from_record(row: ProjectRecord) -> Project:
    return Project(
        project_id=row.id,
        owner_user_id=row.owner_user_id,
        name=row.name,
        description=row.description,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def requirement_profile_from_record(row: RequirementProfileRecord) -> RequirementProfile:
    payload: dict[str, Any] = dict(row.profile)
    payload["requirement_id"] = row.id
    payload["project_id"] = row.project_id
    return RequirementProfile.model_validate(payload)


def requirement_profile_to_json(model: RequirementProfile) -> dict[str, Any]:
    return model.model_dump(mode="json")


def constraint_profile_from_record(row: ConstraintProfileRecord) -> ConstraintProfile:
    payload = dict(row.profile)
    payload["constraint_id"] = row.id
    payload["project_id"] = row.project_id
    payload["requirement_id"] = row.requirement_profile_id
    return ConstraintProfile.model_validate(payload)


def constraint_profile_to_json(model: ConstraintProfile) -> dict[str, Any]:
    return model.model_dump(mode="json")


def capability_block_from_record(row: CapabilityBlockRecord) -> CapabilityBlock:
    payload = dict(row.payload)
    payload.setdefault("capability_id", row.key)
    return CapabilityBlock.model_validate(payload)


def capability_block_to_json(model: CapabilityBlock) -> dict[str, Any]:
    return model.model_dump(mode="json")


def architecture_template_from_record(row: ArchitectureTemplateRecord) -> ArchitectureTemplate:
    payload = dict(row.payload)
    payload.setdefault("template_id", row.key)
    return ArchitectureTemplate.model_validate(payload)


def architecture_template_to_json(model: ArchitectureTemplate) -> dict[str, Any]:
    return model.model_dump(mode="json")


def solution_candidate_from_record(row: SolutionCandidateRecord) -> SolutionCandidate:
    payload = dict(row.payload)
    payload["candidate_id"] = row.id
    payload["project_id"] = row.project_id
    payload["requirement_id"] = row.requirement_profile_id
    return SolutionCandidate.model_validate(payload)


def solution_candidate_to_json(model: SolutionCandidate) -> dict[str, Any]:
    return model.model_dump(mode="json")


def code_snippet_bundle_summary_from_record(row: CodeSnippetBundleRecord) -> CodeSnippetBundleSummary:
    return CodeSnippetBundleSummary(
        bundle_id=row.id,
        project_id=row.project_id,
        runtime_graph_id=row.runtime_graph_id,
        runtime_graph_version=row.runtime_graph_version,
        architecture_pattern=row.architecture_pattern,
        created_at=row.created_at,
    )


def playground_inference_summary_from_record(row: PlaygroundInferenceRunRecord) -> PlaygroundInferenceRun:
    text = row.input_text
    preview = text if len(text) <= 200 else text[:199] + "…"
    return PlaygroundInferenceRun(
        inference_id=row.id,
        project_id=row.project_id,
        runtime_graph_id=row.runtime_graph_id,
        runtime_graph_version=row.runtime_graph_version,
        architecture_pattern=row.architecture_pattern,
        input_preview=preview,
        created_at=row.created_at,
    )


def onboarding_progress_from_record(row: OnboardingTaskProgressRecord) -> OnboardingTaskProgress:
    return OnboardingTaskProgress(
        progress_id=row.id,
        project_id=row.project_id,
        requirement_id=row.requirement_profile_id,
        task_graph_id=row.task_graph_id,
        node_id=row.node_id,
        state=OnboardingTaskState(row.state),
        response=dict(row.response) if row.response else None,
        validation_feedback=dict(row.validation_feedback) if row.validation_feedback else None,
        updated_at=row.updated_at,
    )


def architecture_selection_from_record(row: ArchitectureSelectionRecord) -> ArchitectureSelection:
    return ArchitectureSelection(
        selection_id=row.id,
        project_id=row.project_id,
        requirement_id=row.requirement_profile_id,
        solution_candidate_id=row.solution_candidate_id,
        selected_at=row.selected_at,
    )


def task_graph_from_record(row: TaskGraphRecord) -> TaskGraph:
    payload = dict(row.payload)
    payload["task_graph_id"] = row.id
    payload["project_id"] = row.project_id
    payload["candidate_id"] = row.solution_candidate_id
    return TaskGraph.model_validate(payload)


def task_graph_to_json(model: TaskGraph) -> dict[str, Any]:
    return model.model_dump(mode="json")


def runtime_build_job_from_record(row: RuntimeBuildJobRecord) -> RuntimeBuildJob:
    return RuntimeBuildJob(
        job_id=row.id,
        project_id=row.project_id,
        requirement_id=row.requirement_profile_id,
        solution_candidate_id=row.solution_candidate_id,
        status=RuntimeBuildJobStatus(row.status),
        stage=row.stage,
        error_detail=row.error_detail,
        runtime_graph_id=row.runtime_graph_id,
        runtime_graph_version=row.runtime_graph_version,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def runtime_graph_from_record(row: RuntimeGraphRecord) -> RuntimeGraph:
    payload = dict(row.payload)
    payload["runtime_graph_id"] = row.id
    payload["project_id"] = row.project_id
    payload["version"] = row.version
    payload["candidate_id"] = row.solution_candidate_id
    payload.setdefault("requirement_id", None)
    return RuntimeGraph.model_validate(payload)


def runtime_graph_to_json(model: RuntimeGraph) -> dict[str, Any]:
    return model.model_dump(mode="json")


def evaluation_plan_from_record(row: EvaluationPlanRecord) -> EvaluationPlan:
    payload = dict(row.payload)
    payload["evaluation_plan_id"] = row.id
    payload["project_id"] = row.project_id
    payload["candidate_id"] = row.solution_candidate_id
    return EvaluationPlan.model_validate(payload)


def evaluation_plan_to_json(model: EvaluationPlan) -> dict[str, Any]:
    return model.model_dump(mode="json")


def integration_package_from_record(row: IntegrationPackageRecord) -> IntegrationPackage:
    payload = dict(row.payload)
    payload["package_id"] = row.id
    payload["project_id"] = row.project_id
    payload["candidate_id"] = row.solution_candidate_id
    return IntegrationPackage.model_validate(payload)


def integration_package_to_json(model: IntegrationPackage) -> dict[str, Any]:
    return model.model_dump(mode="json")
