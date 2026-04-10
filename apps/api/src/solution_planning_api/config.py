from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment (12-factor)."""

    model_config = SettingsConfigDict(
        # Support both invocation styles:
        # - from apps/api (reads local .env)
        # - from repo root (reads root .env, then app-specific overrides)
        env_file=(".env", "apps/api/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="AI Solution Planning API")
    app_env: str = Field(default="local")
    debug: bool = Field(default=False)

    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    public_api_base_url: str | None = Field(
        default=None,
        description="Public origin for generated client snippets (e.g. https://api.example.com). "
        "Defaults to http://127.0.0.1:{api_port} when unset.",
    )

    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins (no spaces).",
    )

    # Phase 2+: SQLAlchemy async engine (postgresql+asyncpg://...)
    database_url: str | None = Field(default=None)
    redis_url: str | None = Field(default=None)

    # Phase 3: local JWT auth (replaceable via AccessTokenIssuer implementation)
    jwt_secret_key: str = Field(
        default="dev-only-change-me",
        description="HS256 signing secret; use a long random value in any shared environment.",
    )
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=60 * 24, ge=5, le=60 * 24 * 30)

    # LLM integration layer (provider-agnostic).
    llm_enabled: bool = Field(default=False)
    llm_provider: str = Field(default="disabled", description="disabled|openai_compatible")
    llm_api_base_url: str | None = Field(default=None)
    llm_api_key: str | None = Field(default=None)
    llm_default_model: str = Field(default="gpt-4o-mini")
    llm_timeout_s: float = Field(default=12.0, gt=0.1, le=120.0)
    llm_max_retries: int = Field(default=1, ge=0, le=5)

    @field_validator("jwt_secret_key")
    @classmethod
    def jwt_secret_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("jwt_secret_key must be non-empty")
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def snippet_base_url(self) -> str:
        if self.public_api_base_url and self.public_api_base_url.strip():
            return self.public_api_base_url.strip().rstrip("/")
        return f"http://127.0.0.1:{self.api_port}"

    @property
    def database_url_sync(self) -> str | None:
        """Sync URL for Alembic and other blocking DB tools (postgresql+psycopg://...)."""
        if not self.database_url:
            return None
        url = self.database_url
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "+psycopg", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
