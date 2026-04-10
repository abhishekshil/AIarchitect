import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from solution_planning_api.api.health import router as health_router
from solution_planning_api.api.routes import (
    auth_router,
    candidates_router,
    code_snippets_router,
    onboarding_router,
    playground_router,
    projects_router,
    recommendations_router,
    registry_router,
    requirements_router,
    runtime_build_router,
    selection_router,
)
from solution_planning_api.application.errors import ServiceError
from solution_planning_api.application.services.registry_seeder import ensure_registries_seeded
from solution_planning_api.config import get_settings
from solution_planning_api.infrastructure.auth import BcryptPasswordHasher, JwtAccessTokenIssuer
from solution_planning_api.infrastructure.llm import (
    DisabledLLMProvider,
    InMemoryPromptRegistry,
    LLMOrchestrator,
    LLMTaskPolicy,
    LoggingLLMTelemetry,
    OpenAICompatibleConfig,
    OpenAICompatibleProvider,
)
from solution_planning_api.infrastructure.persistence import (
    create_async_engine_from_settings,
    create_session_factory,
)
from solution_planning_api.infrastructure.requirements import HeuristicRequirementNormalizer
from solution_planning_api.infrastructure.requirements import LLMEnhancedRequirementNormalizer
from solution_planning_api.application.ports.llm import LLMTask

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.password_hasher = BcryptPasswordHasher()
    app.state.token_issuer = JwtAccessTokenIssuer(settings)
    if settings.llm_enabled and settings.llm_provider == "openai_compatible" and settings.llm_api_base_url and settings.llm_api_key:
        provider = OpenAICompatibleProvider(
            OpenAICompatibleConfig(
                base_url=settings.llm_api_base_url,
                api_key=settings.llm_api_key,
                provider_name="openai_compatible",
            )
        )
    else:
        provider = DisabledLLMProvider()
    llm = LLMOrchestrator(
        provider=provider,
        prompts=InMemoryPromptRegistry(),
        telemetry=LoggingLLMTelemetry(),
        task_policies={
            LLMTask.REQUIREMENT_UNDERSTANDING: LLMTaskPolicy(
                model=settings.llm_default_model,
                timeout_s=settings.llm_timeout_s,
                max_retries=settings.llm_max_retries,
                min_confidence=0.55,
            ),
            LLMTask.CLARIFICATION_QUESTIONS: LLMTaskPolicy(
                model=settings.llm_default_model,
                timeout_s=settings.llm_timeout_s,
                max_retries=settings.llm_max_retries,
            ),
            LLMTask.CANDIDATE_EXPLANATION: LLMTaskPolicy(
                model=settings.llm_default_model,
                timeout_s=settings.llm_timeout_s,
                max_retries=settings.llm_max_retries,
            ),
            LLMTask.ONBOARDING_GUIDANCE: LLMTaskPolicy(
                model=settings.llm_default_model,
                timeout_s=settings.llm_timeout_s,
                max_retries=settings.llm_max_retries,
            ),
        },
    )
    app.state.llm_orchestrator = llm
    app.state.requirement_normalizer = LLMEnhancedRequirementNormalizer(
        llm=llm if settings.llm_enabled else None,
        heuristic=HeuristicRequirementNormalizer(),
    )
    engine = create_async_engine_from_settings(settings)
    if engine is None:
        app.state.engine = None
        app.state.session_factory = None
    else:
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)
        async with app.state.session_factory() as session:
            try:
                seeded = await ensure_registries_seeded(session)
                await session.commit()
                if seeded:
                    logger.info(
                        "Registry seeded from bundled YAML (%s capabilities, %s templates)",
                        seeded[0],
                        seeded[1],
                    )
            except Exception:
                await session.rollback()
                raise
    yield
    if getattr(app.state, "engine", None) is not None:
        await app.state.engine.dispose()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)


@app.exception_handler(ServiceError)
async def service_error_handler(_request: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "code": exc.code},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, tags=["health"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(requirements_router, prefix="/api/v1/projects")
app.include_router(candidates_router, prefix="/api/v1/projects")
app.include_router(code_snippets_router, prefix="/api/v1/projects")
app.include_router(recommendations_router, prefix="/api/v1/projects")
app.include_router(selection_router, prefix="/api/v1/projects")
app.include_router(onboarding_router, prefix="/api/v1/projects")
app.include_router(playground_router, prefix="/api/v1/projects")
app.include_router(runtime_build_router, prefix="/api/v1/projects")
app.include_router(registry_router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "status": "ok"}
