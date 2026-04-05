# Foundation Contracts

## Purpose

Phase `01-foundations` establishes the minimum contract surface the rest of the product must extend rather than replace. The goal is to keep auth, session ownership, runtime state, artifacts, and trace events explicit from the beginning.

## Auth Boundary

- The Next.js app uses Clerk as the session authority.
- Protected product routes live under `/workspace`.
- Protection happens in two places:
  - `apps/web/src/proxy.ts` blocks unauthenticated access at the route layer.
  - `apps/web/src/lib/auth.ts` exposes server helpers so layouts and server components can require a user explicitly.
- The Python API currently trusts a Clerk-derived identity bridge via `X-Clerk-User-Id` and `X-Clerk-User-Email`.
- Future phases should replace that bridge with direct token verification, but they must preserve the rule that every persisted record is scoped to one canonical app user.

## Session Envelope

- The primary API contract is the typed session envelope in `apps/api/app/orchestration/contracts.py`.
- A session envelope includes:
  - canonical app user ownership
  - current runtime stage
  - stage history
  - persisted artifacts
  - persisted trace events
  - created/updated timestamps
- The envelope is what the web app should consume. Frontend code should not reach around it and reconstruct session state from raw database shapes.

## Runtime Shell

- The runtime shell lives in `apps/api/app/orchestration/runtime.py`.
- It implements one rule that later phases must keep:
  - a session auto-runs until it reaches an interrupt, approval gate, or completion boundary
- Phase 1 uses a deterministic skeleton:
  - `bootstrap`
  - `jd_intake`
  - `career_intake`
  - `blueprint_review`
  - `draft_review`
  - `complete`
- Later phases can replace the internal logic with LangGraph orchestration, but they should preserve:
  - typed stage keys
  - explicit interrupt reasons
  - persisted stage history
  - explicit `advance` / resume semantics

## Artifact Persistence

- Artifacts are stored in `artifact_records`.
- Every artifact belongs to exactly one session.
- Artifact payloads are JSON and carry stage metadata, allowing future phases to attach:
  - approvals
  - diffs
  - evaluator scorecards
  - draft outputs
- Phase 1 persists question, blueprint, and draft placeholder artifacts to prove the contract shape.
- Future phases should extend artifact kinds rather than create a parallel storage path.

## Trace/Event Model

- Trace events are stored in `trace_event_records`.
- Events capture:
  - stage
  - level
  - human-readable message
  - JSON payload
- Phase 1 uses traces to record transitions and pause points.
- Later phases should keep trace events legible to the user, not only to developers. This is a product feature, not just diagnostics.

## Web Contract

- The web app uses `apps/web/src/lib/api/sessions.ts` as the dedicated session API client.
- The workspace route should render the typed envelope returned by the API.
- If the API is unavailable, the workspace can show a setup/error state, but it should not silently fall back to fake session data.

## Extension Rules

- Add new stage data to the typed contract first, then wire persistence and UI.
- Keep Postgres as the source of truth for session state and approvals.
- Use ChromaDB only as a retrieval aid in later phases, never as the canonical session model.
- Any future evaluator, diff, or approval surface should attach to artifacts or trace events instead of inventing a separate parallel contract.
