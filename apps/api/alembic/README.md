# Alembic migrations

`alembic/env.py` reads `DATABASE_URL` via `Settings.database_url_sync`, which rewrites `+asyncpg` → `+psycopg`. Use the same URL as the app (`postgresql+asyncpg://...`) once `psycopg` is installed (`pip install -e ".[dev]"`).

```bash
cd apps/api
source .venv/bin/activate
export DATABASE_URL="postgresql+asyncpg://aspe:aspe_dev_change_me@localhost:5432/aspe"
alembic upgrade head
```

Match credentials with `docker compose` from the repo root.
