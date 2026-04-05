# Phase 1 Research: Foundations

**Phase:** 1 - Foundations
**Date:** 2026-04-05
**Confidence:** MEDIUM

## Research Focus

Phase 1 should optimize for clean boundaries and future-proof contracts, not polished product behavior. The key architectural risk is choosing repo and runtime patterns that make later vault, orchestration, and UI work harder to integrate.

## Recommended Phase Approach

### Repo / app topology
- Use a repo layout with clear app boundaries:
  - `apps/web` for the Next.js workspace
  - `apps/api` for the FastAPI service
  - `packages/` only if the phase proves a real cross-app contract or frontend utility is needed
- Prefer simple root tooling over premature monorepo complexity. The foundation phase should create a structure that future plans can extend without forcing build-system rewrites.

### Backend foundation
- Start the API with clear service boundaries:
  - auth/session access layer
  - persistence layer
  - orchestration/session runtime shell
- Define typed artifact/state models up front so later phases can plug in JD analysis, vault retrieval, blueprinting, and evaluator stages.

### Persistence baseline
- Use Postgres-backed entities for:
  - user profile linkage
  - sessions
  - artifacts
  - approvals
  - stage events / trace records
- Keep Chroma out of Phase 1 implementation details except for configuration and service boundaries; actual semantic retrieval belongs in Phase 2.

### Frontend baseline
- The first UI should prove:
  - authenticated workspace access
  - session shell rendering
  - placeholder panels for future artifacts
  - trace/event visibility surfaces
- Do not overinvest in final UI polish yet. Phase 4 is where the full product experience gets refined.

## Skill Audit

### GSD Skills

| Skill | Decision | Why |
|-------|----------|-----|
| `gsd-discuss-phase` | Used | Phase context was needed before planning |
| `gsd-plan-phase` | Used | This phase needs executable plan artifacts |
| `gsd-execute-phase` | Deferred | Use after the plan files are ready |
| `gsd-verify-work` | Deferred | Use after implementation exists |
| `gsd-add-tests` | Deferred | Phase 1 tests should be generated after implementation lands |
| `gsd-progress` | Available | Useful for later routing, but not required to author these artifacts |
| `gsd-next` | Available | Useful after planning/execution checkpoints |
| `gsd-new-project` | Used | Required because the repo had no `.planning/` scaffold |

### Non-GSD Skills

| Skill | Decision | Why |
|-------|----------|-----|
| `brainstorming` | Already satisfied | Product design and tradeoffs were discussed in detail before execution |
| `frontend-design` | Deferred | Full UI treatment belongs in Phase 4, not the foundation shell |
| `vercel-react-best-practices` | Deferred | Becomes relevant when real React components land |
| `openai-docs` | Skipped for now | Phase 1 is mostly structure and infra, not current OpenAI API integration details |

## Risks To Address In Planning

1. Avoid inventing a cross-language shared-schema system before there is a real need.
2. Keep auth and app authorization boundaries explicit from the start.
3. Make trace/event persistence simple enough to ship now but structured enough for later artifact UI.
4. Keep local developer setup ergonomic; Phase 1 should not create brittle bootstrapping friction.

## Planning Implications

- Plan 1 should create the repo/app skeleton and tooling conventions.
- Plan 2 should wire auth and persistence without overreaching into full feature behavior.
- Plan 3 should establish orchestration contracts, session APIs, and the trace/event model.

---
*Phase research completed: 2026-04-05*
