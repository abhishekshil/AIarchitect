"""Alembic environment — sync engine using `Settings.database_url_sync` (psycopg)."""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from solution_planning_api.config import get_settings
from solution_planning_api.infrastructure.persistence import orm_models  # noqa: F401
from solution_planning_api.infrastructure.persistence.base import MappedBase

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = MappedBase.metadata


def get_url() -> str:
    settings = get_settings()
    url = settings.database_url_sync
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Use postgresql+asyncpg:// for the app and ensure "
            "database_url_sync resolves (asyncpg → psycopg for Alembic)."
        )
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
