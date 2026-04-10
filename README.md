# AI Solution Planning Engine (ASPE)

Monorepo for a **general AI solution planning engine**: natural-language requirements → capability mapping → architecture options → onboarding → runtime workflow → inference/testing → integration-ready snippets.

## Repository layout

| Path | Purpose |
|------|---------|
| `apps/api` | FastAPI backend (domain / application / infrastructure / API layers) |
| `apps/web` | Next.js (App Router) + TypeScript frontend |
| `docker-compose.yml` | Full local stack (API, Web, PostgreSQL, Redis) |
| `.env.example` | Cross-cutting env documentation (copy fragments into per-app `.env`) |

## Prerequisites

- **Node.js** 20+ and **pnpm** 9+ (frontend)
- **Python** 3.12+ (backend)
- **Docker** + Docker Compose (recommended for full local stack)

### Paths containing `:` (colon)

pnpm treats `:` as a `PATH` separator on Unix. If your clone path includes a colon (e.g. `AI:MLArchitect`), `pnpm exec` and default `PATH`-based binaries can fail. This repo uses **explicit `node …/next` and `node …/prettier` scripts** so `pnpm dev:web`, `pnpm lint`, and `pnpm format` still work. Prefer cloning to a path without `:` when possible.

## Quick start (Phase 18)

### Option A: run everything with Docker Compose (recommended)

1. Copy root env:

   ```bash
   cp .env.example .env
   ```

2. Build and start all services:

   ```bash
   docker compose up -d --build
   ```

3. Verify:

   - API health: [http://localhost:8000/health](http://localhost:8000/health)
   - API docs (when `API_DEBUG=true`): [http://localhost:8000/docs](http://localhost:8000/docs)
   - Web app: [http://localhost:3000](http://localhost:3000)

4. Useful commands:

   ```bash
   docker compose logs -f api web
   docker compose ps
   docker compose down
   ```

### Option B: run API/Web on host, DB/Redis in Docker

1. **Infrastructure**

   ```bash
   docker compose up -d postgres redis
   ```

2. **Backend** — from `apps/api`:

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   cp .env.example .env
   alembic upgrade head
   uvicorn solution_planning_api.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend** — from repo root:

   ```bash
   pnpm install
   pnpm dev:web
   ```

4. **Sanity checks**

   - API: [http://localhost:8000/health](http://localhost:8000/health)
   - API docs (debug): [http://localhost:8000/docs](http://localhost:8000/docs) — set `DEBUG=true` in `apps/api/.env`
   - Web: [http://localhost:3000](http://localhost:3000)

## Tooling

- **Python**: Ruff (lint + format), Mypy (strict) — see `apps/api/pyproject.toml`
- **JS/TS**: ESLint (Next.js defaults) + Prettier at repo root
- **Dev Containers**: `.devcontainer/devcontainer.json` (Node + Python)

## Tests and CI

- Backend critical-flow tests: `python3 -m pytest apps/api/tests`
- Frontend fast unit tests: `pnpm --filter web test`
- CI skeleton: `.github/workflows/ci.yml` runs lint, type-check, and tests for both API and Web on push/PR.

## Maintainability Notes

- Application services should depend on domain/application modules and ports, not concrete infrastructure modules.
- For planned post-MVP cleanup tasks and boundary improvements, see `docs/post-mvp-tech-debt.md`.

## Environment variables

- **Root** `.env.example`: compose interpolation source for local stack (`API_DATABASE_URL`, `API_REDIS_URL`, `NEXT_PUBLIC_API_URL`, ports, JWT, etc.).
- **`apps/api/.env`**: host-run API settings (`DATABASE_URL`, `REDIS_URL`, `CORS_ORIGINS`, `PUBLIC_API_BASE_URL`, auth).
- **`apps/web/.env.local`**: host-run web settings (`NEXT_PUBLIC_API_URL`).
- **Security note**: all example values are development-only defaults; replace secrets before shared/staging usage. Never commit real `.env` files.

## Why this structure

- **`apps/*`**: clear service boundaries; later we can add `packages/contracts` for OpenAPI-generated types or shared JSON Schema without coupling UI to Python imports.
- **Backend layers** (`domain` / `application` / `infrastructure` / `api`): keeps registries, planning graphs, and adapters swappable (Postgres, Redis, S3, vector backends) as phases land.
- **Config-driven growth**: new capabilities and templates attach via registries and data, not rewrites of a single “workflow builder” spine.

## Phase roadmap

Implementation follows locked phases (see project brief). **Phase 1** establishes the monorepo, tooling, Docker-friendly deps, and skeleton apps only.
