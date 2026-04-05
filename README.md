# Resume Agent

Resume Agent is a chat-first, agentic resume optimization platform. The product is being built as a GSD-native project with a `Next.js` frontend, a `FastAPI + LangGraph` backend, and planning artifacts tracked in `.planning/`.

## Repository Layout

- `apps/web` — Next.js workspace shell
- `apps/api` — FastAPI service skeleton
- `.planning/` — GSD project context, requirements, roadmap, and phase artifacts

## Local Setup

### Web app

```bash
pnpm install
pnpm dev:web
```

The web app runs from `apps/web`.

### API app

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e "./apps/api[dev]"
pnpm dev:api
```

The API entrypoint is `apps/api/app/main.py`.

## Current Status

This repo is in Phase 1: Foundations. The current goal is to establish the runtime split, auth/data foundations, and orchestration shell that later phases extend.

## Workflow

This project is run through GSD. The canonical artifacts live in `.planning/`, and each phase is expected to go through:

1. `gsd-discuss-phase`
2. `gsd-plan-phase`
3. `gsd-execute-phase`
4. `gsd-verify-work`
