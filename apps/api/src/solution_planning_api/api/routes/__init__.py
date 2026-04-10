from solution_planning_api.api.routes.auth import router as auth_router
from solution_planning_api.api.routes.candidates import router as candidates_router
from solution_planning_api.api.routes.code_snippets import router as code_snippets_router
from solution_planning_api.api.routes.onboarding import router as onboarding_router
from solution_planning_api.api.routes.playground import router as playground_router
from solution_planning_api.api.routes.projects import router as projects_router
from solution_planning_api.api.routes.recommendations import router as recommendations_router
from solution_planning_api.api.routes.registry import router as registry_router
from solution_planning_api.api.routes.requirements import router as requirements_router
from solution_planning_api.api.routes.runtime_build import router as runtime_build_router
from solution_planning_api.api.routes.selection import router as selection_router

__all__ = [
    "auth_router",
    "candidates_router",
    "code_snippets_router",
    "onboarding_router",
    "playground_router",
    "projects_router",
    "recommendations_router",
    "registry_router",
    "requirements_router",
    "runtime_build_router",
    "selection_router",
]
