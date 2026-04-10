"""Canonical domain models (Pydantic) — planning engine vocabulary."""

from solution_planning_api.domain.architecture_pattern import infer_architecture_pattern_from_runtime_graph
from solution_planning_api.domain.architecture_selection import ArchitectureSelection
from solution_planning_api.domain.architecture_template import ArchitectureTemplate
from solution_planning_api.domain.capability_block import CapabilityBlock
from solution_planning_api.domain.code_snippet_bundle import CodeSnippetBundleSummary
from solution_planning_api.domain.common import JsonObject, utc_now
from solution_planning_api.domain.constraint_profile import ConstraintProfile
from solution_planning_api.domain.evaluation_plan import (
    EvaluationPlan,
    EvaluationSuite,
    MetricThreshold,
)
from solution_planning_api.domain.onboarding import (
    OnboardingTaskProgress,
    OnboardingTaskState,
)
from solution_planning_api.domain.inference_playground import PlaygroundInferenceRun
from solution_planning_api.domain.integration_package import (
    CodeSnippet,
    EndpointDefinition,
    IntegrationPackage,
)
from solution_planning_api.domain.requirement_profile import RequirementProfile
from solution_planning_api.domain.runtime_build import RuntimeBuildJob, RuntimeBuildJobStatus
from solution_planning_api.domain.runtime_component import RuntimeComponentType
from solution_planning_api.domain.runtime_graph import (
    RuntimeGraph,
    RuntimeGraphEdge,
    RuntimeGraphNode,
)
from solution_planning_api.domain.solution_candidate import SolutionCandidate
from solution_planning_api.domain.task_graph import TaskGraph, TaskGraphEdge, TaskGraphNode
from solution_planning_api.domain.workspace import Project, User

__all__ = [
    "ArchitectureSelection",
    "CodeSnippetBundleSummary",
    "ArchitectureTemplate",
    "CapabilityBlock",
    "CodeSnippet",
    "ConstraintProfile",
    "EndpointDefinition",
    "EvaluationPlan",
    "EvaluationSuite",
    "IntegrationPackage",
    "infer_architecture_pattern_from_runtime_graph",
    "JsonObject",
    "MetricThreshold",
    "OnboardingTaskProgress",
    "PlaygroundInferenceRun",
    "OnboardingTaskState",
    "Project",
    "RequirementProfile",
    "RuntimeBuildJob",
    "RuntimeBuildJobStatus",
    "RuntimeComponentType",
    "RuntimeGraph",
    "RuntimeGraphEdge",
    "RuntimeGraphNode",
    "SolutionCandidate",
    "TaskGraph",
    "TaskGraphEdge",
    "TaskGraphNode",
    "User",
    "utc_now",
]
