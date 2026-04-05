---
phase: 02-career-vault
plan: 02
subsystem: ingestion
tags: [career-vault, ingestion, session-runtime, nextjs, checkpoint-review]
requires:
  - phase: 02-career-vault
    provides: canonical vault schema, typed vault routes
provides:
  - Seed import and guided role-capture ingestion paths
  - Vault interview sessions attached to the resumable orchestration runtime
  - Minimal workspace surface for vault prompts, checkpoints, and canonical role visibility
affects: [phase-2, phase-3, runtime, workspace]
tech-stack:
  added: [vault-ingestion-runtime, vault-workspace-client]
  patterns: [single-story capture, checkpoint-before-persist, vault-mode session bootstrap]
key-files:
  created: [apps/web/src/lib/api/vault.ts]
  modified:
    [
      apps/api/app/vault/contracts.py,
      apps/api/app/vault/ingestion.py,
      apps/api/app/api/routes/vault.py,
      apps/api/app/orchestration/contracts.py,
      apps/api/app/orchestration/runtime.py,
      apps/web/src/lib/api/sessions.ts,
      apps/web/src/app/(workspace)/workspace/page.tsx,
    ]
key-decisions:
  - "Run vault ingestion through the same session shell as the resume workflow instead of inventing a side-channel pipeline."
  - "Stop the user at a story checkpoint artifact before writing canonical vault memory."
  - "Keep the web surface narrow in this phase: show vault prompts, checkpoint state, and stored roles without building the final interaction UX yet."
patterns-established:
  - "Vault sessions can bootstrap directly into a dedicated vault flow by setting runtime.flow = vault_ingestion."
  - "Checkpoint approval and canonical persistence stay separate so later phases can add richer review/edit affordances."
requirements-completed: [VAULT-01, VAULT-02, VAULT-04]
duration: 64min
completed: 2026-04-05
---

# Phase 2: Career Vault Summary

**Import-first and interview-first Career Vault ingestion attached to the runtime shell, with minimal workspace visibility for prompts and story checkpoints**

## Performance

- **Duration:** 64 min
- **Started:** 2026-04-05T23:00:00-07:00
- **Completed:** 2026-04-06T00:04:00-07:00
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- Added seed import, guided role capture, and typed checkpoint response contracts for focused single-story vault ingestion.
- Attached vault ingestion to resumable session runtime boundaries so prompts, interruptions, approvals, and persistence share one shell.
- Added a small workspace client and vault-aware workspace page that can bootstrap a vault session, surface prompt/checkpoint state, and show canonical vault roles.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add seed import and guided ingestion services** - `2e6b978` (feat)
2. **Task 2: Attach vault ingestion to the session runtime** - `5feadf2`, `3e0ac06` (feat)
3. **Task 3: Add minimal workspace support for vault ingestion** - `1b0e4c6`, `e45532e`, `8bbaf66` (feat/chore)

## Files Created/Modified
- `apps/api/app/vault/contracts.py` - Ingestion/session request and checkpoint response contracts
- `apps/api/app/vault/ingestion.py` - Seed import, guided capture, checkpoint, and statement extraction helpers
- `apps/api/app/api/routes/vault.py` - Vault import/interview routes and vault interview session endpoints
- `apps/api/app/orchestration/contracts.py` - Vault stage keys and checkpoint approval input contract
- `apps/api/app/orchestration/runtime.py` - Vault ingestion runtime flow, checkpoint artifact handling, and persistence boundary
- `apps/web/src/lib/api/vault.ts` - Authenticated server-only vault API client for the web app
- `apps/web/src/app/(workspace)/workspace/page.tsx` - Minimal vault-aware workspace surface
- `apps/web/src/lib/api/sessions.ts` - Frontend stage keys updated for vault runtime stages

## Decisions Made
- Used `?mode=vault` as the smallest useful entrypoint for vault session bootstrapping in the existing workspace route.
- Treated the checkpoint artifact as the canonical review surface for now, rather than inventing a separate vault review page in this phase.
- Listed canonical roles alongside the current session so the workspace proves long-term memory and in-flight capture can coexist.

## Deviations from Plan

### Auto-fixed Issues

**1. Frontend typecheck picked up stale `.next` type artifacts after an accidental duplicate page filename**
- **Found during:** Web verification after the workspace page change
- **Issue:** `pnpm typecheck:web` initially referenced generated `.next/types/* 2.ts` paths from a stray duplicate file that had already been removed.
- **Fix:** Removed the duplicate source file, let `next build` regenerate current types, and reran the standalone typecheck successfully.
- **Files modified:** None tracked; generated cache refreshed
- **Verification:** `pnpm lint:web`, `pnpm build:web`, `pnpm typecheck:web`

---

**Total deviations:** 1 auto-fixed (generated type cache issue)
**Impact on plan:** No scope change. The implementation plan stayed intact.

## Issues Encountered
- The frontend session type union lagged behind the new backend vault stages and needed a small contract update before the vault-aware page could stay typed.

## User Setup Required

None - the existing Phase 1 Clerk and Neon configuration was sufficient for this plan.

## Next Phase Readiness
- `02-03` can now implement retrieval and eligibility rules on top of canonical vault entities, explicit review states, and visible vault session artifacts.
- Phase 3 can later reuse the same session/artifact structure when resume-stage agents query approved vault memory.

---
*Phase: 02-career-vault*
*Completed: 2026-04-05*
