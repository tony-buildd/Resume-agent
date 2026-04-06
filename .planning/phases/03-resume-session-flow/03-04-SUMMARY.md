---
phase: 03-resume-session-flow
plan: 04
subsystem: evaluation-and-reruns
tags: [resume-session, evaluation, scorecard, rerun-routing, draft-review]
requires:
  - phase: 03-resume-session-flow
    provides: blueprint and draft package artifacts
provides:
  - Typed evaluator scorecard for fit, evidence support, specificity, and overstatement risk
  - Draft-review interrupt boundary for accept vs targeted revision
  - Earliest-stage rerun routing with trace visibility
affects: [phase-3, runtime, evaluation, reruns, review-state]
tech-stack:
  added: [evaluation-service]
  patterns: [scorecard-artifact, targeted-rerun, review-before-complete]
key-files:
  created:
    [
      apps/api/app/orchestration/evaluation.py,
      .planning/phases/03-resume-session-flow/03-04-SUMMARY.md,
    ]
  modified:
    [
      apps/api/app/orchestration/contracts.py,
      apps/api/app/orchestration/runtime.py,
      apps/api/app/api/routes/sessions.py,
    ]
key-decisions:
  - "Score the draft package immediately at `draft_review` so the user always sees a scorecard before the session completes."
  - "Route revision requests to the evaluator's earliest affected stage instead of restarting from JD intake."
  - "Keep rerun reasons visible in trace events so targeted revisions are inspectable."
patterns-established:
  - "Draft review now supports accept and revision actions through typed request flags."
  - "Evaluation scorecards persist as first-class artifacts alongside the draft package."
requirements-completed: [FLOW-06, WRIT-03, WRIT-04]
duration: 34min
completed: 2026-04-05
---

# Phase 3: Resume Session Flow Summary

**Draft review now scores the package before completion and can reroute the session to the earliest weak stage instead of starting over**

## Performance

- **Duration:** 34 min
- **Started:** 2026-04-05T16:33:00-07:00
- **Completed:** 2026-04-05T17:07:00-07:00
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Added typed evaluation scorecards covering fit, evidence support, specificity, and overstatement risk.
- Changed `draft_review` from an auto-complete boundary into a review gate that persists both the draft package and evaluator scorecard.
- Added targeted revision routing so a draft-review revision request jumps back to the earliest affected stage and records the reason in trace history.
- Extended the session advance contract so clients can accept the draft review or request a targeted rerun explicitly.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add evaluator scoring contracts and service** - `e0581fe` (feat)
2. **Task 2: Add earliest-stage rerun routing** - `6e9143b` (feat)

## Files Created/Modified

- `apps/api/app/orchestration/contracts.py` - Draft-review controls and evaluation scorecard contracts
- `apps/api/app/orchestration/evaluation.py` - Heuristic scoring for fit, evidence, specificity, and overstatement risk
- `apps/api/app/orchestration/runtime.py` - Draft-review interrupt gate and targeted rerun routing
- `apps/api/app/api/routes/sessions.py` - API forwarding for accept/revision flags

## Decisions Made

- Evaluation remains deterministic for now so revision routing stays predictable and testable.
- A revision request now prefers `career_intake` when the draft is missing supporting evidence, and `blueprint_review` when the story selection/specificity is the weaker link.
- The runtime immediately pauses after generating the scorecard so later UI work can render the review state without changing orchestration semantics.

## Deviations from Plan

### Auto-fixed Issues

**1. Revision-flow verification originally assumed a custom transition string**

- **Found during:** API-level rerun verification
- **Issue:** The runtime correctly rerouted to `career_intake` and immediately interrupted there, so the response transition reflected the interruption message rather than a synthetic rerun string.
- **Fix:** Updated the verification expectations to assert the new stage and rerun trace event instead of relying on a transition string.
- **Files modified:** None tracked
- **Verification:** Rerun flow passed after checking stage, interrupt reason, and trace payload

---

**Total deviations:** 1 auto-fixed verification expectation
**Impact on plan:** No scope change.

## Verification

- `PYTHONPATH=apps/api .venv/bin/python -c "from app.orchestration.evaluation import evaluate_resume_package; print('eval-import-ok')"`
- API-level session flow using `TestClient` and a temporary SQLite database:
  - create session
  - advance through JD review, interrogation, blueprint approval
  - confirm `draft_review` pauses with both `draft-package` and `evaluation-scorecard` artifacts
  - accept draft review and confirm session completes
  - request revision on a second session and confirm reroute to `career_intake`
  - confirm trace history includes `rerunTarget`

## Next Phase Readiness

- Phase 3 is now complete and ready for a phase-level UAT closeout.
- Phase 4 can build the visible review UI on top of stable `blueprint`, `draft-package`, and `evaluation-scorecard` artifacts.

---

_Phase: 03-resume-session-flow_
_Completed: 2026-04-05_
