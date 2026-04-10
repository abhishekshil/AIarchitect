# solution-planning-api

FastAPI service for the AI Solution Planning Engine. Layering:

- `api/` — HTTP routers, schemas, deps (Phase 3+)
- `application/` — use cases / orchestration (Phase 2+)
- `domain/` — entities, value objects, domain services (Phase 2+)
- `infrastructure/` — DB, cache, queues, external adapters (Phase 2+)

## Setup

```bash
cd apps/api
python3.12 -m venv .venv   # Python 3.12+ required (see pyproject.toml)
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -U pip
pip install -e ".[dev]"
```

## Run

```bash
uvicorn solution_planning_api.main:app --reload --host 0.0.0.0 --port 8000
```

Or from repo root with Docker Compose:

```bash
docker compose up -d --build api postgres redis
```

## Lint / typecheck

```bash
ruff check src && ruff format --check src
mypy src
```

## Database migrations

PostgreSQL must be running. Ensure `DATABASE_URL` uses `postgresql+asyncpg://...` (Alembic rewrites to `psycopg` automatically).

```bash
alembic upgrade head
```

## Domain vs persistence

- **Domain**: `src/solution_planning_api/domain/` — Pydantic canonical objects (`RequirementProfile`, `SolutionCandidate`, graphs, etc.).
- **ORM**: `src/solution_planning_api/infrastructure/persistence/orm_models.py` — tables and FK graph; JSONB columns hold serialized domain payloads validated in the application layer.
- **Mappers**: `infrastructure/persistence/mappers.py` — translate rows ↔ domain (row ids / FKs override embedded JSON for consistency).

## Capability & architecture registries (Phase 5)

Bundled YAML under `src/solution_planning_api/registry_data/` defines **capabilities** and **architecture templates**. On startup, if either DB table is empty, rows are **upserted** (same keys refresh payload).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/registry/capabilities` | List `CapabilityBlock` entries (metadata: inputs, outputs, prerequisites, profiles, …) |
| GET | `/api/v1/registry/capabilities/{capability_id}` | One capability |
| GET | `/api/v1/registry/architecture-templates` | List `ArchitectureTemplate` entries |
| GET | `/api/v1/registry/architecture-templates/{template_id}` | One template |

All routes require `Authorization: Bearer`.

**Extend without core rewrites:** add/edit YAML, restart the API (or add a future admin “reload” job). Read ports: `CapabilityRegistryReader`, `ArchitectureTemplateRegistryReader` (`application/ports/registries.py`).

## Requirements intake (Phase 4)

All routes require `Authorization: Bearer <token>` and project ownership.

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/v1/projects/{project_id}/requirements` | Submit `{"raw_text": "..."}` → heuristic normalization → versioned `RequirementProfile` (+ optional `ConstraintProfile`) |
| GET | `/api/v1/projects/{project_id}/requirements/latest` | Latest revision + constraint (if any) |
| GET | `/api/v1/projects/{project_id}/requirements` | List revisions (summaries) |
| GET | `/api/v1/projects/{project_id}/requirements/{requirement_id}` | One revision + constraint |
| GET | `/api/v1/projects/{project_id}/requirements/{requirement_id}/constraints` | Constraint only (404 if none) |

**Extensibility:** `RequirementNormalizer` (`application/ports/requirement_normalization.py`) is wired from `app.state.requirement_normalizer` (default `HeuristicRequirementNormalizer`). Swap in an LLM-backed class with the same async `normalize()` contract.

## Auth & projects (Phase 3)

- **Register**: `POST /api/v1/auth/register` with JSON `{ "email", "password" }` (password ≥ 8 chars).
- **Login**: `POST /api/v1/auth/login` → `{ "access_token", "token_type", "expires_in" }`.
- **Me**: `GET /api/v1/auth/me` with header `Authorization: Bearer <token>`.
- **Projects** (Bearer required): `GET/POST /api/v1/projects`, `GET/PATCH/DELETE /api/v1/projects/{project_id}`.

Enterprise auth: swap `JwtAccessTokenIssuer` / `BcryptPasswordHasher` via new implementations of `AccessTokenIssuer` and `PasswordHasher` (`application/ports/auth.py`) and wire them in `main.py` lifespan.

```bash
# Example (after migrate + run server)
curl -sS -X POST localhost:8000/api/v1/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"longsecret"}'
curl -sS -X POST localhost:8000/api/v1/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","password":"longsecret"}'
```

Copy `.env.example` to `.env` and adjust.

When running API inside Docker Compose, use service hostnames in URLs (for example `postgres` and `redis`) instead of `localhost`.
