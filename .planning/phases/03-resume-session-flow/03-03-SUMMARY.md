---
phase: 03-resume-session-flow
plan: 03
subsystem: blueprint-and-drafting
tags: [resume-session, blueprint, drafting, markdown-resume, interview-notes]
requires:
  - phase: 03-resume-session-flow
    provides: canonical session context from interrogation
provides:
  - Typed narrative blueprint contracts and deterministic blueprint selection
  - Draft package assembly with markdown resume and interview notes
  - Runtime enforcement that blueprint approval happens before draft generation
affects: [phase-3, runtime, blueprint, drafting, artifact-payloads]
tech-stack:
  added: [blueprint-service, drafting-service]
  patterns: [draft-safe-selection, one-page-budgeting, artifact-first-drafting]
key-files:
  created:
    [
      apps/api/app/orchestration/blueprint.py,
      apps/api/app/orchestration/drafting.py,
      .planning/phases/03-resume-session-flow/03-03-SUMMARY.md,
    ]
  modified:
    [
      apps/api/app/orchestration/contracts.py,
      apps/api/app/orchestration/runtime.py,
    ]
key-decisions:
  - "Blueprint generation reads only `draftSafeRoles` from the vault, never questioning-safe inferred material."
  - "The runtime stores the typed blueprint in session state and requires explicit approval before the draft package is generated."
  - "Draft review now persists one package artifact containing the markdown resume plus interview notes instead of a placeholder stub."
patterns-established:
  - "Narrative blueprint records now carry selected roles, selected bullets, omitted signals, and one-page section budgets."
  - "Draft package records now bundle markdown resume output with talking points and concern-handling notes."
requirements-completed: [FLOW-04, WRIT-01, WRIT-02]
duration: 41min
completed: 2026-04-05
---

# Phase 3: Resume Session Flow Summary

**Blueprint review now selects draft-safe evidence into a one-page strategy, and draft review produces a real resume package instead of a placeholder**

## Performance

- **Duration:** 41 min
- **Started:** 2026-04-05T15:51:00-07:00
- **Completed:** 2026-04-05T16:32:00-07:00
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Added typed blueprint and draft-package contracts so the orchestration runtime can pass structured strategist/writer outputs instead of placeholder payloads.
- Built a deterministic blueprinting service that ranks draft-safe vault evidence against the approved JD and selects a one-page role and bullet budget.
- Added a drafting service that emits a markdown resume, interview talking points, and concern-handling notes from the approved blueprint.
- Replaced the `draft_review` placeholder artifact with a real `draft-package` artifact and enforced blueprint approval before draft generation.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add blueprint contracts and selection logic** - `a995309`, `ffcccc2` (feat)
2. **Task 2: Add draft package assembly and runtime wiring** - `b67949b`, `49fded8` (feat)

## Files Created/Modified
- `apps/api/app/orchestration/contracts.py` - Typed blueprint and draft-package records
- `apps/api/app/orchestration/blueprint.py` - Draft-safe strategist selection and one-page blueprint generation
- `apps/api/app/orchestration/drafting.py` - Markdown resume and interview-notes package assembly
- `apps/api/app/orchestration/runtime.py` - Blueprint approval gate and final package generation

## Decisions Made
- Kept blueprint selection deterministic for now so the runtime remains inspectable even when provider access is degraded.
- Limited strategist input to approved JD context plus draft-safe vault evidence to preserve the project’s truth boundary.
- Stored the final writer output as one package artifact because later evaluation can score a single coherent payload.

## Deviations from Plan

### Auto-fixed Issues

**1. Initial verification script referenced non-existent helper modules**
- **Found during:** API-level end-to-end verification
- **Issue:** The first local verification script used paths that are not present in this repo (`app.users`, `app.api.auth`).
- **Fix:** Reworked the verification harness to import the actual session auth/user helpers from `apps/api/app/api/routes/sessions.py`.
- **Files modified:** None tracked
- **Verification:** End-to-end session flow re-ran successfully after the script fix

---

**Total deviations:** 1 auto-fixed verification issue
**Impact on plan:** No scope change.

## Verification

- `pnpm typecheck:web`
- `PYTHONPATH=apps/api .venv/bin/python -c "from app.orchestration.blueprint import build_narrative_blueprint; from app.orchestration.drafting import build_resume_package; print('imports-ok')"`
- API-level session flow using `TestClient` and a temporary SQLite database:
  - create session
  - submit JD
  - approve JD analysis
  - confirm interrogation prompt exists
  - answer the highest-impact gap question
  - confirm `blueprint_review` artifact contains selected draft-safe roles
  - approve blueprint
  - confirm `draft-package` artifact contains `markdownResume`, `talkingPoints`, and `concernHandlingNotes`
  - confirm session completes after package generation

## Next Phase Readiness
- `03-04` can now score a concrete draft package instead of a placeholder artifact.
- Targeted reruns can attach to real blueprint and draft artifacts without redefining strategist/writer contracts.

---
*Phase: 03-resume-session-flow*
*Completed: 2026-04-05*
