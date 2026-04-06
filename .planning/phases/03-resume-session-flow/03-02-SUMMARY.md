---
phase: 03-resume-session-flow
plan: 02
subsystem: interrogation
tags:
  [resume-session, interrogation, canonical-context, vault-retrieval, runtime]
requires:
  - phase: 03-resume-session-flow
    provides: approved JD analysis and research artifacts
provides:
  - Typed interrogation prompt contract and gap-selection service
  - One-question-at-a-time runtime behavior for career intake
  - Canonical session-context artifact built from user answers
affects: [phase-3, runtime, interrogation, canonical-state]
tech-stack:
  added: [interrogation-service, canonical-session-context]
  patterns:
    [
      single-gap-question,
      vault-informed-questioning,
      canonical-answer-persistence,
    ]
key-files:
  created: [apps/api/app/orchestration/interrogation.py]
  modified:
    [
      apps/api/app/orchestration/contracts.py,
      apps/api/app/orchestration/runtime.py,
    ]
key-decisions:
  - "Use questioning-safe vault retrieval to choose the weakest-covered JD requirement rather than asking a generic experience dump question."
  - "Persist user answers into a canonical session-context artifact so downstream stages read stable state instead of transient prompt history."
  - "Keep interrogation inside the existing `career_intake` stage for now while enforcing one active question at a time."
patterns-established:
  - "Interrogation prompts now carry `whyItMatters`, `targetRequirement`, and `responseKey` as typed fields."
  - "Blueprinting can inspect canonical session context keys instead of reparsing freeform answers."
requirements-completed: [FLOW-02, FLOW-05]
duration: 38min
completed: 2026-04-06
---

# Phase 3: Resume Session Flow Summary

**Career intake now asks one vault-informed gap question at a time and persists the answer as canonical session state before blueprinting**

## Performance

- **Duration:** 38 min
- **Started:** 2026-04-06T02:33:00-07:00
- **Completed:** 2026-04-06T03:11:00-07:00
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Added a typed interrogation prompt contract and a gap-selection service that reads JD analysis, research summary, and questioning-safe vault retrieval.
- Replaced the generic `career_intake` question with a single highest-impact interrogation prompt that explains why the missing signal matters.
- Persisted user answers into a canonical `session-context` artifact and runtime snapshot so later stages can treat them as stable downstream truth.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add interrogation contracts and gap-selection logic** - `7c39369`, `ba41fe2` (feat)
2. **Task 2: Persist canonical user edits and approvals** - `51b95e1` (feat)

## Files Created/Modified

- `apps/api/app/orchestration/contracts.py` - Typed interrogation prompt contract
- `apps/api/app/orchestration/interrogation.py` - Gap-selection and canonical-context helpers
- `apps/api/app/orchestration/runtime.py` - Vault-informed question generation and canonical session-context persistence

## Decisions Made

- Used the weakest-covered top JD requirement as the interrogation target instead of asking for a generic “most relevant experience.”
- Treated the user’s answer as canonical session context immediately, rather than waiting for a later editing UI phase.
- Kept the output narrow: one active question, one canonical context artifact, then move to blueprinting.

## Deviations from Plan

### Auto-fixed Issues

**1. Initial verification payload used an invalid vault `sourceType`**

- **Found during:** API-level interrogation verification
- **Issue:** The test seed data used `approved` as a source type, which is a review state, not a provenance enum.
- **Fix:** Corrected the verification payload to use a valid source type and re-ran the flow.
- **Files modified:** None tracked
- **Verification:** End-to-end `career_intake` flow check after correcting the test payload

---

**Total deviations:** 1 auto-fixed verification issue
**Impact on plan:** No scope change.

## Verification

- API-level session flow using `TestClient` and a temporary SQLite database:
  - create session
  - submit JD
  - approve JD analysis
  - confirm exactly one `interrogation-question` artifact exists
  - answer the question
  - confirm transition to `blueprint_review`
  - confirm `session-context` artifact stores canonical answer keys

## Next Phase Readiness

- `03-03` can now generate the narrative blueprint from approved JD analysis plus canonical session context instead of relying on raw answers.
- Later UI work can render interrogation question rationale and canonical context without changing backend contracts.

---

_Phase: 03-resume-session-flow_
_Completed: 2026-04-06_
