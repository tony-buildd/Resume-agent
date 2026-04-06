---
phase: 02-career-vault
plan: 01
subsystem: database
tags: [career-vault, postgres, sqlalchemy, fastapi, provenance]
requires:
  - phase: 01-foundations
    provides: auth boundary, postgres wiring, typed API shell
provides:
  - Canonical vault ORM entities for companies, roles, stories, facts, and bullet candidates
  - Typed vault contracts and serialization helpers
  - User-scoped create/list vault routes
affects: [phase-2, phase-3, persistence, retrieval]
tech-stack:
  added: [vault-orm, vault-contracts]
  patterns:
    [fact-vs-bullet separation, review-state fields, typed nested role envelope]
key-files:
  created:
    [
      apps/api/app/vault/contracts.py,
      apps/api/app/vault/service.py,
      apps/api/app/api/routes/vault.py,
    ]
  modified: [apps/api/app/db/models.py, apps/api/app/main.py]
key-decisions:
  - "Keep facts and bullet candidates as separate entities linked through supporting fact relationships."
  - "Use a nested role envelope as the first vault API surface instead of exposing raw table-shaped CRUD."
  - "Preserve user ownership through the existing AppUser boundary rather than introducing a second auth model."
patterns-established:
  - "Role-level and story-level memory are both preserved, but serialization keeps them distinct."
  - "Vault APIs follow the same typed-contract pattern established for sessions in Phase 1."
requirements-completed: [VAULT-03, VAULT-04, VAULT-05]
duration: 47min
completed: 2026-04-05
---

# Phase 2: Career Vault Summary

**Canonical Career Vault schema and typed FastAPI routes for user-scoped roles, project stories, facts, provenance, and reusable bullet candidates**

## Performance

- **Duration:** 47 min
- **Started:** 2026-04-05T22:10:00-07:00
- **Completed:** 2026-04-05T22:57:00-07:00
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added normalized ORM entities for the Career Vault with provenance/review state and fact-to-bullet linkage.
- Added typed request/response contracts plus a vault service layer to create and serialize nested role trees.
- Exposed user-scoped vault create/list routes and verified role/story/fact/bullet round-tripping with TestClient.

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend the database model with canonical vault entities** - `8c808aa` (feat)
2. **Task 2: Add typed vault contracts and service-layer primitives** - `c2fca7e` (feat)
3. **Task 3: Expose user-scoped vault routes** - `2713ddb` (feat)

**Plan metadata:** `2713ddb` (current execution checkpoint)

## Files Created/Modified

- `apps/api/app/db/models.py` - Canonical vault entities and supporting fact linkage table
- `apps/api/app/vault/contracts.py` - Typed nested vault input/output models
- `apps/api/app/vault/service.py` - Role-tree persistence and serialization helpers
- `apps/api/app/api/routes/vault.py` - User-scoped create/list vault routes
- `apps/api/app/main.py` - API router registration for the vault surface

## Decisions Made

- Stored project-story facts and role-level facts separately while still keeping them under the same role for later retrieval.
- Used `supportingFactClientKeys` in creation payloads so bullets can link to facts immediately without requiring multiple API round trips.
- Kept company creation simple for now and deferred deduplication/merge behavior to later ingestion work.

## Deviations from Plan

### Auto-fixed Issues

**1. Fact and bullet relationship records were duplicated in memory**

- **Found during:** Local API verification for nested role creation
- **Issue:** The service was assigning relationships and appending children, which produced duplicate serialized facts/bullets.
- **Fix:** Removed the extra append path and filtered role-level serialization to exclude story-level children.
- **Files modified:** `apps/api/app/vault/service.py`
- **Verification:** TestClient create/list round-trip with nested role/story payload
- **Committed in:** `2713ddb`

---

**Total deviations:** 1 auto-fixed (relationship duplication)
**Impact on plan:** No scope change. The fix was required to keep the typed envelope trustworthy.

## Issues Encountered

- The initial verification payload mixed review-state and source-type values, which was corrected during API testing before final verification.

## User Setup Required

None - the existing Phase 1 database configuration was sufficient for this plan.

## Next Phase Readiness

- `02-02` can now build import and interview-first ingestion on top of stable canonical vault entities and routes.
- `02-03` can later layer retrieval/indexing logic onto the persisted fact and bullet model without redefining the schema.

---

_Phase: 02-career-vault_
_Completed: 2026-04-05_
