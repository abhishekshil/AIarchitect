# web

Next.js (App Router) frontend for the AI Solution Planning Engine.

## Setup

From repo root:

```bash
pnpm install
```

Copy `.env.example` to `.env.local` when you need a public API base URL for fetch helpers.

## Scripts

| Command | Description |
|---------|-------------|
| `pnpm dev` | Dev server (default port 3000) |
| `pnpm build` | Production build |
| `pnpm start` | Run production server |
| `pnpm lint` | ESLint (Next.js config) |

Repo root also exposes `pnpm dev:web` via the `web` workspace filter.

## Docker workflow

From repo root:

```bash
cp .env.example .env.local
docker compose up -d --build web api postgres redis
```

The web app is available at `http://localhost:3000` and expects the API at `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`).
