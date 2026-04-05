---
phase: 02-career-vault
plan: 03
subsystem: retrieval
tags: [career-vault, chromadb, retrieval, review-state-filtering, semantic-recall]
requires:
  - phase: 02-career-vault
    provides: canonical vault schema, ingestion runtime, checkpointed role capture
provides:
  - Chroma-backed indexing adapter for long-form vault notes
  - Retrieval services that separate draft-safe and questioning-safe outputs
  - Typed retrieval endpoint and web client contract for later session integration
affects: [phase-2, phase-3, retrieval, questioning, drafting]
tech-stack:
  added: [chromadb, vault-retrieval-service, typed-recall-client]
  patterns: [postgres-source-of-truth, semantic-sidecar-index, review-state-aware-retrieval]
key-files:
  created:
    [apps/api/app/vault/indexing.py, apps/api/app/vault/retrieval.py]
  modified:
    [
      apps/api/pyproject.toml,
      apps/api/app/config.py,
      apps/api/app/vault/contracts.py,
      apps/api/app/api/routes/vault.py,
      apps/web/src/lib/api/vault.ts,
    ]
key-decisions:
  - "Keep semantic indexing in a dedicated Chroma adapter and never treat it as canonical career storage."
  - "Return two explicit retrieval views from the same role tree: draft-safe for writing and questioning-safe for follow-up prompts."
  - "Exclude rejected material from all retrieval views while allowing inferred material only in questioning-safe outputs."
patterns-established:
  - "Vault retrieval can now combine deterministic relational filtering with semantic note recall."
  - "Later resume stages can depend on a typed vault recall contract instead of bespoke role queries."
requirements-completed: [VAULT-05, VAULT-06]
duration: 61min
completed: 2026-04-06
---

# Phase 2: Career Vault Summary

**Review-state-aware retrieval and semantic indexing for reusable career memory, with explicit separation between draft-safe and questioning-safe vault recall**

## Performance

- **Duration:** 61 min
- **Started:** 2026-04-05T23:55:00-07:00
- **Completed:** 2026-04-06T00:56:00-07:00
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments
- Added Chroma configuration and an isolated indexing adapter that turns canonical role trees into semantic note documents without changing the Postgres source-of-truth model.
- Added retrieval contracts and services that filter the same role into `draftSafeRoles` and `questioningSafeRoles` according to review state and draft eligibility.
- Exposed the retrieval contract through FastAPI and the Next.js server-side vault client so later workspace and session phases can consume it directly.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add Chroma-backed indexing for long-form vault notes** - `4e927f4`, `5a49bac`, `e6901c4` (build/feat)
2. **Task 2: Add retrieval services with review-state filtering** - `505825e`, `ca46b8e`, `807c07f` (feat)
3. **Task 3: Expose typed retrieval access to the web app** - `e8ad393` (feat)

## Files Created/Modified
- `apps/api/pyproject.toml` - Added `chromadb` dependency
- `apps/api/app/config.py` - Added Chroma backend settings
- `apps/api/app/vault/indexing.py` - Isolated Chroma indexing and semantic query adapter
- `apps/api/app/vault/contracts.py` - Retrieval request/response and semantic match contracts
- `apps/api/app/vault/retrieval.py` - Review-state-aware role filtering and recall service
- `apps/api/app/api/routes/vault.py` - Typed vault retrieval endpoint
- `apps/web/src/lib/api/vault.ts` - Typed vault retrieval client for the web app

## Decisions Made
- Kept indexing opt-in through backend settings while defaulting the adapter on for local development so semantic recall is available without extra product wiring.
- Ranked relational role matches with lightweight in-memory scoring for this phase, deferring more advanced ranking or reranking to later orchestration work.
- Used the same nested role record shape for retrieval outputs, but filtered the child facts and bullets per trust boundary instead of inventing separate write-only DTOs.

## Deviations from Plan

### Auto-fixed Issues

**1. Internal Pydantic field names differed from API aliases**
- **Found during:** Retrieval and indexing implementation
- **Issue:** Server-side Pydantic records expose snake_case field names internally, while the API uses camelCase aliases. The first pass used the alias names directly.
- **Fix:** Updated indexing and retrieval services to consume the internal snake_case fields while preserving camelCase serialization at the API boundary.
- **Files modified:** `apps/api/app/vault/indexing.py`, `apps/api/app/vault/retrieval.py`
- **Verification:** Service-level retrieval test and API-level `TestClient` retrieval check

---

**Total deviations:** 1 auto-fixed (internal field-name mismatch)
**Impact on plan:** No scope change. The fix was required to keep the typed retrieval layer trustworthy.

## Issues Encountered
- The local Python environment lagged behind the new dependency declaration, so `chromadb` had to be installed into the existing `.venv` before semantic verification could run.

## User Setup Required

None beyond the project’s normal dependency installation flow. The current `.env` configuration was sufficient for verification.

## Next Phase Readiness
- Phase 2 is complete. Phase 3 can now query the vault through one typed retrieval surface without risking inferred facts leaking into resume drafts.
- `03-01` can consume `draftSafeRoles`, `questioningSafeRoles`, and semantic note matches while implementing JD analysis and cited research.

---
*Phase: 02-career-vault*
*Completed: 2026-04-06*
