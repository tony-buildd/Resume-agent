# Local Setup

This repo is a monorepo with:
- `apps/web` — Next.js frontend
- `apps/api` — FastAPI backend
- `.planning/` — GSD project operating artifacts

## Prerequisites

- `node` 20+
- `pnpm` 10+
- `python` 3.12+
- a local or remote Postgres database
- Clerk keys

Optional but recommended:
- an OpenAI API key for live JD analysis/research

## 1. Install dependencies

From the repo root:

```bash
pnpm install
python3 -m venv .venv
source .venv/bin/activate
pip install -e "./apps/api[dev]"
```

## 2. Create your local env file

Copy the example file:

```bash
cp .env.example .env
```

Then fill in the required values described in [environment.md](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/docs/developer/environment.md).

## 3. Start the backend

```bash
source .venv/bin/activate
pnpm dev:api
```

Expected default URL:

```text
http://127.0.0.1:8000
```

## 4. Start the frontend

In another terminal:

```bash
pnpm dev:web
```

Expected default URL:

```text
http://127.0.0.1:3000
```

## 5. Verify the stack

Backend import check:

```bash
source .venv/bin/activate
pnpm check:api
```

Frontend quality checks:

```bash
pnpm typecheck:web
pnpm lint:web
pnpm build:web
```

## Common Notes

- `DATABASE_URL` must use the `postgresql+psycopg://` prefix for the current backend setup.
- The web app expects Clerk auth to be configured before `/workspace` behaves normally.
- If `OPENAI_API_KEY` is missing or the configured model is unavailable, the backend falls back to deterministic heuristics for the research stages.

## First Working Loop

1. Start API
2. Start web
3. Open `/workspace`
4. Verify auth works
5. Verify session creation and stage rendering work
6. Use `.planning/STATE.md` to see the current active phase before making changes
