---
phase: 03-resume-session-flow
plan: 01
subsystem: jd-analysis
tags: [resume-session, openai, responses-api, jd-analysis, research, approval-gate]
requires:
  - phase: 01-foundations
    provides: session runtime, typed artifacts, auth boundary
  - phase: 02-career-vault
    provides: draft-safe and questioning-safe vault retrieval surface
provides:
  - OpenAI provider adapter for structured Responses API calls
  - Typed JD analysis and research summary contracts
  - JD-analysis approval gate in the main resume session runtime
affects: [phase-3, runtime, research, approvals]
tech-stack:
  added: [openai-sdk, responses-adapter, jd-research-service]
  patterns: [provider-fallback, staged-approval, structured-analysis-artifacts]
key-files:
  created:
    [
      apps/api/app/llm/__init__.py,
      apps/api/app/llm/openai_client.py,
      apps/api/app/orchestration/research.py,
    ]
  modified:
    [
      apps/api/pyproject.toml,
      apps/api/app/config.py,
      apps/api/app/orchestration/contracts.py,
      apps/api/app/orchestration/runtime.py,
      apps/api/app/api/routes/sessions.py,
      apps/web/src/lib/api/sessions.ts,
      .env.example,
    ]
key-decisions:
  - "Keep the OpenAI SDK behind a small Responses adapter so runtime logic never depends on raw SDK response shapes."
  - "Pause the main resume flow at a dedicated JD analysis review stage before moving into career interrogation."
  - "If provider calls fail or a model is unavailable, fall back to deterministic JD heuristics instead of crashing the session."
patterns-established:
  - "Structured JD analysis and research summary are now separate artifacts under one approval boundary."
  - "Provider-level schema and model access problems are handled in the integration layer, not leaked into the runtime."
requirements-completed: [RSCH-01, RSCH-03, FLOW-03]
duration: 92min
completed: 2026-04-06
---

# Phase 3: Resume Session Flow Summary

**JD analysis and research artifacts now run on the main session shell, with an explicit approval boundary before the resume flow continues**

## Performance

- **Duration:** 92 min
- **Started:** 2026-04-06T01:00:00-07:00
- **Completed:** 2026-04-06T02:32:00-07:00
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments
- Added OpenAI provider configuration plus a thin Responses API adapter for structured outputs and optional raw response metadata.
- Added a JD analysis/research service that can use OpenAI when available and fall back to deterministic heuristics when provider access fails.
- Extended the main session runtime so JD submission produces `jd-analysis` and `research-summary` artifacts, pauses for approval, and only then moves to `career_intake`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add provider configuration and OpenAI adapter** - `65c04e1`, `0704901`, `e7cc427`, `4efaf45` (build/feat)
2. **Task 2: Add JD analysis and research stage services** - `e70aad4`, `e33fcf3`, `047fab3`, `e811845` (feat/fix)
3. **Task 3: Attach JD analysis approval to the runtime** - `a1a01da`, `7e8447c`, `f837a66`, `4c90fd4` (feat/fix/chore/docs)

## Files Created/Modified
- `apps/api/pyproject.toml` - Added OpenAI SDK dependency
- `apps/api/app/config.py` - Added OpenAI provider settings
- `apps/api/app/llm/openai_client.py` - Responses API adapter and strict schema normalization
- `apps/api/app/orchestration/contracts.py` - JD analysis review stage, approval flag, and research contracts
- `apps/api/app/orchestration/research.py` - JD analysis and research summary generation with provider fallback
- `apps/api/app/orchestration/runtime.py` - JD analysis artifact creation, approval gate, and runtime stage transition
- `apps/api/app/api/routes/sessions.py` - Forwarded `approveJdAnalysis` through the session route
- `apps/web/src/lib/api/sessions.ts` - Added the new stage type on the web client side
- `.env.example` - Added OpenAI env settings

## Decisions Made
- Treated the JD-analysis approval boundary as a first-class runtime stage instead of hiding it inside `jd_intake`.
- Stored the structured JD analysis and the strategic research summary as separate artifacts so the workspace can later render them independently.
- Left the provider path resilient: missing key, inaccessible model, or schema mismatch now degrade to heuristics rather than hard-failing the user session.

## Deviations from Plan

### Auto-fixed Issues

**1. OpenAI strict JSON schema requirements rejected raw Pydantic schemas**
- **Found during:** API-level JD flow verification
- **Issue:** The Responses API rejected the structured-output schema because nested object nodes were missing `additionalProperties: false`.
- **Fix:** Normalized JSON schemas in the OpenAI adapter before sending them to the API.
- **Files modified:** `apps/api/app/llm/openai_client.py`
- **Verification:** Reran the JD session lifecycle check after the adapter fix

**2. The configured OpenAI project key could not access `gpt-5.2`**
- **Found during:** API-level JD flow verification
- **Issue:** Provider calls returned `model_not_found` / permission errors for the configured model.
- **Fix:** Hardened the JD research service to catch provider failures and fall back to deterministic heuristics.
- **Files modified:** `apps/api/app/orchestration/research.py`
- **Verification:** End-to-end JD session lifecycle completed successfully without provider hard failure

**3. JD-analysis artifacts were not persisting their approved status**
- **Found during:** JD approval lifecycle verification
- **Issue:** The session advanced, but the `jd-analysis` and `research-summary` artifacts stayed `candidate`.
- **Fix:** Approved the stage/kind artifacts directly instead of relying on cached runtime artifact IDs.
- **Files modified:** `apps/api/app/orchestration/runtime.py`
- **Verification:** Re-ran the JD session lifecycle and confirmed both artifacts end in `approved`

---

**Total deviations:** 3 auto-fixed
**Impact on plan:** No scope change. All fixes were required to make the approval gate and provider layer production-safe.

## Issues Encountered
- Local verification revealed a real provider-access mismatch: the environment had an OpenAI key available, but not access to the configured default model.

## User Setup Required

- To enable live OpenAI-backed JD analysis and web-search research, set `OPENAI_API_KEY`.
- If your project does not have access to `gpt-5.2`, set `OPENAI_MODEL` to a model your project can use.

## Verification

- `pnpm typecheck:web`
- `PYTHONPATH=apps/api .venv/bin/python -c 'from app.main import app; from app.orchestration.research import heuristic_jd_analysis; ...'`
- API-level JD session lifecycle using `TestClient` and a temporary SQLite database:
  - create session
  - pause for JD input
  - submit JD
  - pause for JD analysis approval with `jd-analysis` and `research-summary` artifacts
  - approve JD analysis
  - confirm transition to `career_intake`

## Next Phase Readiness
- `03-02` can now build interrogation and canonical session edits on top of approved JD analysis artifacts instead of raw job-description text.
- The workspace already has enough contract surface to render JD analysis and research artifacts later in Phase 4.

---
*Phase: 03-resume-session-flow*
*Completed: 2026-04-06*
