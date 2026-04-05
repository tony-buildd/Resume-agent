---
phase: 01-foundations
plan: 02
subsystem: auth
tags: [clerk, postgres, sqlalchemy, fastapi, nextjs]
requires:
  - phase: 01-foundations
    provides: repo-level pnpm workspace and runnable web/api shells
provides:
  - Clerk-backed protected workspace boundary
  - User-owned session persistence primitives in Postgres models
  - Typed session lifecycle API routes with ownership checks
affects: [phase-1, orchestration, api, auth, persistence]
tech-stack:
  added: [clerk, sqlalchemy, psycopg, pydantic-settings]
  patterns: [server auth helper module, user-scoped session envelope, app-level settings cache]
key-files:
  created: [apps/web/src/lib/auth.ts, apps/web/src/app/sign-in/[[...sign-in]]/page.tsx, apps/web/src/app/sign-up/[[...sign-up]]/page.tsx, apps/api/app/config.py, apps/api/app/db/session.py, apps/api/app/db/models.py, apps/api/app/api/routes/health.py, apps/api/app/api/routes/sessions.py, .planning/phases/01-foundations/01-02-USER-SETUP.md]
  modified: [apps/web/src/app/layout.tsx, apps/web/src/app/page.tsx, apps/web/src/proxy.ts, apps/web/package.json, apps/api/app/main.py, apps/api/pyproject.toml]
key-decisions:
  - "Use Clerk server-side auth helpers in a shared module instead of scattering auth checks through pages."
  - "Model only user, session, artifact, and trace-event ownership in phase 1; defer vault-specific schema."
  - "Use a header-based Clerk identity bridge for the API until direct token verification is added in a later phase."
patterns-established:
  - "Protected web routes live under /workspace and are guarded both by Clerk proxy middleware and layout-level requireUser checks."
  - "Session lifecycle endpoints return typed envelopes anchored to a canonical AppUser record."
requirements-completed: [AUTH-01, AUTH-02, AUTH-03]
duration: 58min
completed: 2026-04-05
---

# Phase 1: Foundations Summary

**Clerk-protected workspace shell with user-scoped session, artifact, and trace persistence primitives exposed through typed FastAPI routes**

## Performance

- **Duration:** 58 min
- **Started:** 2026-04-05T15:20:00-07:00
- **Completed:** 2026-04-05T16:18:00-07:00
- **Tasks:** 3
- **Files modified:** 13

## Accomplishments
- Added Clerk-backed auth boundaries, sign-in/up routes, and a protected workspace shell in the Next.js app.
- Added backend settings, SQLAlchemy database wiring, and the initial user/session/artifact/trace persistence models.
- Exposed typed health and session lifecycle routes that enforce user ownership and prepare the orchestration layer for phase `01-03`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add frontend auth boundaries for the workspace shell** - `8dba19e` (feat)
2. **Task 2: Add backend config and Postgres session persistence** - `fba2124`, `0c3b256`, `6175df2` (build/feat)
3. **Task 3: Expose minimal API routes for health and session lifecycle** - `b2f18eb` (feat)

**Plan metadata:** `9283eee` (docs: add phase 01-02 setup requirements)

## Files Created/Modified
- `apps/web/src/lib/auth.ts` - Centralized Clerk server auth helpers and workspace redirect behavior
- `apps/web/src/proxy.ts` - Protected workspace route matcher using Clerk middleware
- `apps/web/src/app/(workspace)/layout.tsx` - Authenticated workspace shell layout
- `apps/web/src/app/page.tsx` - Landing page CTA logic driven by live auth state
- `apps/web/src/app/sign-in/[[...sign-in]]/page.tsx` - Clerk sign-in route
- `apps/web/src/app/sign-up/[[...sign-up]]/page.tsx` - Clerk sign-up route
- `apps/api/app/config.py` - Cached application settings
- `apps/api/app/db/session.py` - SQLAlchemy engine/session setup and database initialization
- `apps/api/app/db/models.py` - User, session, artifact, and trace-event models
- `apps/api/app/api/routes/sessions.py` - Typed create/read session endpoints
- `apps/api/app/api/routes/health.py` - API health route
- `.planning/phases/01-foundations/01-02-USER-SETUP.md` - External setup needed for live Clerk/Postgres verification

## Decisions Made
- Kept the web auth surface server-first so session-dependent UI can be rendered without client-only guards.
- Used a single `AppUser` ownership model to anchor every persisted session artifact in later phases.
- Deliberately stopped short of adding direct Clerk JWT verification to the API until the orchestration contract is in place.

## Deviations from Plan

### Auto-fixed Issues

**1. Clerk component export mismatch on the landing page**
- **Found during:** Post-implementation verification
- **Issue:** `SignedIn` and `SignedOut` are not exported by the installed Clerk package version.
- **Fix:** Switched the landing page to use the shared server auth helper and conditional rendering.
- **Files modified:** `apps/web/src/app/page.tsx`
- **Verification:** `pnpm typecheck:web`, `pnpm build:web`
- **Committed in:** `28a255b`

---

**Total deviations:** 1 auto-fixed (package/API mismatch)
**Impact on plan:** No scope change. The fix aligned the implementation with the installed Clerk version.

## Issues Encountered
- Local API verification initially failed because the editable backend package dependencies had not been installed into the repo virtualenv. Installing `apps/api` into `./.venv` resolved the import/runtime checks.
- End-to-end auth and persistence verification is still gated on real Clerk keys and a reachable Postgres database.

## User Setup Required

**External services require manual configuration.** See [01-02-USER-SETUP.md](./01-02-USER-SETUP.md) for:
- Environment variables to add
- Clerk and Postgres setup steps
- Verification commands

## Next Phase Readiness
- `01-03` can now layer the first orchestration runtime and typed session envelope on top of stable auth and persistence primitives.
- Remaining live verification requires your `CLERK_SECRET_KEY`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, and a working `DATABASE_URL`.

---
*Phase: 01-foundations*
*Completed: 2026-04-05*
