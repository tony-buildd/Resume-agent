# Deployment

This repo is currently best thought of as two deployable services plus one managed database:

- `apps/web` — Next.js frontend
- `apps/api` — FastAPI backend
- `Postgres` — canonical database

Recommended default stack for this project:
- frontend: Vercel
- backend: Railway, Render, Fly.io, or another Python-friendly host
- database: Neon Postgres

## Service Responsibilities

### Frontend

The frontend is responsible for:
- Clerk-authenticated workspace access
- rendering session artifacts
- sending review actions to the backend

Required frontend env:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `NEXT_PUBLIC_CLERK_SIGN_IN_URL`
- `NEXT_PUBLIC_CLERK_SIGN_UP_URL`
- `RESUME_AGENT_API_URL` or equivalent public API URL

### Backend

The backend is responsible for:
- sessions
- artifacts and traces
- career vault persistence
- orchestration runtime
- provider-backed JD analysis / drafting / evaluation

Required backend env:
- `CLERK_SECRET_KEY`
- `DATABASE_URL`
- optional `OPENAI_API_KEY`
- optional `OPENAI_MODEL`
- optional `OPENAI_REASONING_EFFORT`

### Database

The database stores:
- users
- sessions
- artifacts
- traces
- career vault structures

Current expectation:
- use Postgres with a `postgresql+psycopg://` connection string in app config

## Recommended Deployment Shape

### Option A: Split deploys

Recommended for clarity:
- deploy `apps/web` separately as the frontend
- deploy the FastAPI app separately as the backend
- point the frontend at the backend base URL

Why:
- clear failure boundaries
- simpler debugging
- easier to scale frontend and backend independently

### Option B: Single-platform deployment

Possible if you want convenience over strict separation:
- host web + API on a platform that supports both services cleanly

This can work, but the repo should still conceptually treat them as separate deployable units.

## Secrets Rules

- Do not commit real secrets
- Keep `.env.example` as placeholders only
- Rotate leaked or pasted keys immediately
- Document new required env vars in both `.env.example` and `docs/developer/environment.md`

## Pre-Deploy Checks

Before deploying:

```bash
pnpm typecheck:web
pnpm lint:web
pnpm build:web
source .venv/bin/activate
pnpm check:api
```

## Post-Deploy Checks

After deployment:

1. confirm frontend loads
2. confirm Clerk auth redirects work
3. confirm backend health/import checks pass
4. confirm session creation works
5. confirm the workspace can reach the API
6. confirm database-backed session persistence still works

## Current Limitation

This repo documents a deployment path, but it does not yet include a full CI/CD pipeline or one-click infra automation. That can be added later once the hosting target is locked.
