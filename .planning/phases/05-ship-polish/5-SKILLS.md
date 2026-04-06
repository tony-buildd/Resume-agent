# Phase 5 Skill Audit

## Purpose

Track the deliberate skill review for the Ship / Polish phase before planning and implementation begin.

## GSD Skills

### Used

- `gsd-discuss-phase` - Used as the workflow model for gathering shipping and onboarding scope.
- `gsd-plan-phase` - Reflected in the plan breakdown that turns the final milestone into concrete doc and ops slices.
- `gsd-ship` - Considered as the target workflow shape for the final release-oriented phase, even if not invoked yet.

### Skipped

- `gsd-execute-phase` - Deferred until the Phase 5 plans are written.
- `gsd-verify-work` - Deferred until the shipping/onboarding artifacts exist.
- `gsd-ui-review` - No longer primary; frontend review belongs to the completed Phase 4 work.
- `gsd-add-tests` - Unlikely to be the main tool for a docs/ops phase.

## Non-GSD Skills

### Used

- `vercel-react-best-practices` - Relevant only insofar as deployment/readiness guidance touches the Next.js app shape.
- `neon-postgres` - Relevant for documenting the current Postgres setup and connection expectations accurately.
- `openai-docs` - Relevant only if provider setup guidance needs official wording later; not required for the first planning pass.

### Skipped

- `frontend-design` - The core UI work is already done.
- `interaction-design` - Phase 5 is primarily about docs, deployment, and operating guidance.
- `baseline-ui` - Not relevant to a docs/release hardening phase.

## Deferred Follow-Up

- Revisit `gsd-ship` once Phase 5 docs and release scaffolding are in place.
- Pull deployment-specific skills only if a concrete hosting target is chosen during implementation.
