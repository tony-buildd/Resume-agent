# Developer Onboarding

## What This Repo Is

Resume Agent is an agentic resume optimization product with:
- a persistent career vault
- a multi-stage JD-to-resume orchestration backend
- a chat-first, inspectable frontend workspace

This repo is not run as an ad hoc coding project. It uses `.planning/` as a project operating system.

## Main Areas

### `apps/web`

The Next.js app that renders:
- the authenticated workspace
- stage-aware artifact panels
- review actions
- diff views
- trace summaries

### `apps/api`

The FastAPI app that handles:
- users and sessions
- runtime stages
- artifacts and trace events
- career vault persistence
- JD analysis, blueprinting, drafting, and evaluation

### `.planning/`

The canonical GSD layer:
- `PROJECT.md`
- `REQUIREMENTS.md`
- `ROADMAP.md`
- `STATE.md`
- phase context, plans, summaries, and UAT files

## First Files To Read

1. [README.md](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/README.md)
2. [.planning/PROJECT.md](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/.planning/PROJECT.md)
3. [.planning/ROADMAP.md](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/.planning/ROADMAP.md)
4. [.planning/STATE.md](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/.planning/STATE.md)
5. [docs/architecture/foundation-contracts.md](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/docs/architecture/foundation-contracts.md)

## How To Start Working

1. Follow [local-setup.md](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/docs/developer/local-setup.md)
2. Confirm env values using [environment.md](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/docs/developer/environment.md)
3. Check `.planning/STATE.md` for the current active phase
4. Read the relevant phase context and plan files
5. Work in small commits and push each step

## Current Product Shape

Completed:
- foundations
- career vault
- resume session flow
- frontend workspace

Current remaining milestone:
- ship / polish

## Working Expectations

- Keep product-facing docs concise and high-signal
- Keep implementation and operating detail in `docs/`
- Treat `.planning/` as the source of workflow truth
- Do not bypass the GSD lifecycle for meaningful project work

## If You Need Fast Orientation

Use this order:

1. `README.md` for product context
2. `.planning/STATE.md` for current position
3. `.planning/ROADMAP.md` for milestone structure
4. the latest phase summary files for what was just completed
