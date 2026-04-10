from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from solution_planning_api.application.errors import UnauthorizedError
from solution_planning_api.application.ports.auth import AccessTokenIssuer
from solution_planning_api.application.ports.candidate_planning import CandidatePlanningEngine
from solution_planning_api.application.ports.runtime_graph_building import RuntimeGraphBuilder
from solution_planning_api.application.ports.task_graph_building import TaskGraphBuilder
from solution_planning_api.application.ports.requirement_normalization import RequirementNormalizer
from solution_planning_api.application.services.architecture_selection_service import (
    ArchitectureSelectionService,
)
from solution_planning_api.application.onboarding.llm_guidance import LLMOnboardingGuidance
from solution_planning_api.application.services.onboarding_service import OnboardingService
from solution_planning_api.application.services.auth_service import AuthService
from solution_planning_api.application.services.code_snippet_service import CodeSnippetService
from solution_planning_api.application.services.candidate_service import CandidateService
from solution_planning_api.application.services.project_service import ProjectService
from solution_planning_api.application.services.registry_query_service import RegistryQueryService
from solution_planning_api.application.services.requirement_service import RequirementService
from solution_planning_api.application.services.inference_playground_service import InferencePlaygroundService
from solution_planning_api.application.services.runtime_build_service import RuntimeBuildService
from solution_planning_api.config import Settings, get_settings
from solution_planning_api.domain import User
from solution_planning_api.infrastructure.persistence.repositories import (
    SqlAlchemyArchitectureSelectionRepository,
    SqlAlchemyArchitectureTemplateRegistryRepository,
    SqlAlchemyCapabilityRegistryRepository,
    SqlAlchemyConstraintProfileRepository,
    SqlAlchemyOnboardingProgressRepository,
    SqlAlchemyCodeSnippetBundleRepository,
    SqlAlchemyPlaygroundInferenceRepository,
    SqlAlchemyProjectRepository,
    SqlAlchemyRequirementProfileRepository,
    SqlAlchemyRuntimeBuildJobRepository,
    SqlAlchemyRuntimeGraphRepository,
    SqlAlchemySolutionCandidateRepository,
    SqlAlchemyTaskGraphRepository,
    SqlAlchemyUserRepository,
)
from solution_planning_api.infrastructure.inference.mock_playground import MockPlaygroundInferenceSimulator
from solution_planning_api.infrastructure.planning import (
    HeuristicCandidatePlanningEngine,
    HeuristicRuntimeGraphBuilder,
    HeuristicTaskGraphBuilder,
)
from solution_planning_api.infrastructure.planning.llm_candidate_explainer import LLMCandidateExplainer

http_bearer = HTTPBearer(auto_error=True)


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    factory = getattr(request.app.state, "session_factory", None)
    if factory is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured",
        )
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


def get_app_settings() -> Settings:
    return get_settings()


def get_auth_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> AuthService:
    return AuthService(
        users=SqlAlchemyUserRepository(session),
        password_hasher=request.app.state.password_hasher,
        token_issuer=request.app.state.token_issuer,
        settings=settings,
    )


def get_project_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ProjectService:
    return ProjectService(SqlAlchemyProjectRepository(session))


def get_architecture_selection_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ArchitectureSelectionService:
    projects = ProjectService(SqlAlchemyProjectRepository(session))
    builder: TaskGraphBuilder = HeuristicTaskGraphBuilder()
    onboarding = SqlAlchemyOnboardingProgressRepository(session)
    return ArchitectureSelectionService(
        projects=projects,
        requirements=SqlAlchemyRequirementProfileRepository(session),
        constraints=SqlAlchemyConstraintProfileRepository(session),
        candidates=SqlAlchemySolutionCandidateRepository(session),
        selections=SqlAlchemyArchitectureSelectionRepository(session),
        task_graphs=SqlAlchemyTaskGraphRepository(session),
        templates=SqlAlchemyArchitectureTemplateRegistryRepository(session),
        capabilities=SqlAlchemyCapabilityRegistryRepository(session),
        builder=builder,
        onboarding_progress=onboarding,
    )


def get_onboarding_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OnboardingService:
    projects = ProjectService(SqlAlchemyProjectRepository(session))
    llm = getattr(request.app.state, "llm_orchestrator", None)
    return OnboardingService(
        projects=projects,
        requirements=SqlAlchemyRequirementProfileRepository(session),
        selections=SqlAlchemyArchitectureSelectionRepository(session),
        task_graphs=SqlAlchemyTaskGraphRepository(session),
        progress=SqlAlchemyOnboardingProgressRepository(session),
        guidance=LLMOnboardingGuidance(llm),
    )


def runtime_build_service_from_session(session: AsyncSession) -> RuntimeBuildService:
    projects = ProjectService(SqlAlchemyProjectRepository(session))
    builder: RuntimeGraphBuilder = HeuristicRuntimeGraphBuilder()
    return RuntimeBuildService(
        projects=projects,
        requirements=SqlAlchemyRequirementProfileRepository(session),
        selections=SqlAlchemyArchitectureSelectionRepository(session),
        candidates=SqlAlchemySolutionCandidateRepository(session),
        templates=SqlAlchemyArchitectureTemplateRegistryRepository(session),
        task_graphs=SqlAlchemyTaskGraphRepository(session),
        runtime_graphs=SqlAlchemyRuntimeGraphRepository(session),
        jobs=SqlAlchemyRuntimeBuildJobRepository(session),
        builder=builder,
    )


def get_runtime_build_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RuntimeBuildService:
    return runtime_build_service_from_session(session)


def inference_playground_service_from_session(session: AsyncSession) -> InferencePlaygroundService:
    projects = ProjectService(SqlAlchemyProjectRepository(session))
    return InferencePlaygroundService(
        projects=projects,
        runtime_graphs=SqlAlchemyRuntimeGraphRepository(session),
        history=SqlAlchemyPlaygroundInferenceRepository(session),
        simulator=MockPlaygroundInferenceSimulator(),
    )


def get_inference_playground_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> InferencePlaygroundService:
    return inference_playground_service_from_session(session)


def get_code_snippet_service(
    session: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> CodeSnippetService:
    projects = ProjectService(SqlAlchemyProjectRepository(session))
    return CodeSnippetService(
        projects=projects,
        runtime_graphs=SqlAlchemyRuntimeGraphRepository(session),
        bundles=SqlAlchemyCodeSnippetBundleRepository(session),
        snippet_base_url=settings.snippet_base_url,
    )


def get_candidate_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CandidateService:
    llm = getattr(request.app.state, "llm_orchestrator", None)
    engine: CandidatePlanningEngine = HeuristicCandidatePlanningEngine(
        explainer=LLMCandidateExplainer(llm),
    )
    projects = ProjectService(SqlAlchemyProjectRepository(session))
    return CandidateService(
        projects=projects,
        requirements=SqlAlchemyRequirementProfileRepository(session),
        constraints=SqlAlchemyConstraintProfileRepository(session),
        candidates=SqlAlchemySolutionCandidateRepository(session),
        capability_registry=SqlAlchemyCapabilityRegistryRepository(session),
        template_registry=SqlAlchemyArchitectureTemplateRegistryRepository(session),
        engine=engine,
    )


def get_registry_query_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RegistryQueryService:
    return RegistryQueryService(
        capabilities=SqlAlchemyCapabilityRegistryRepository(session),
        templates=SqlAlchemyArchitectureTemplateRegistryRepository(session),
    )


def get_requirement_service(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RequirementService:
    normalizer = cast(RequirementNormalizer, request.app.state.requirement_normalizer)
    projects = ProjectService(SqlAlchemyProjectRepository(session))
    return RequirementService(
        projects=projects,
        requirements=SqlAlchemyRequirementProfileRepository(session),
        constraints=SqlAlchemyConstraintProfileRepository(session),
        normalizer=normalizer,
    )


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    issuer: AccessTokenIssuer = request.app.state.token_issuer
    try:
        user_id = issuer.verify_and_get_user_id(credentials.credentials)
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    user = await SqlAlchemyUserRepository(session).get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
