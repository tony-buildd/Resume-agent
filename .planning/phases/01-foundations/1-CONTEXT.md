# Phase 1: Foundations - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Set up the project foundation for Resume Agent: repo/app skeleton, frontend/backend split, auth wiring, database setup, orchestration harness shell, and the event/trace model that later phases build on. This phase does not implement the career vault, full JD-to-resume flow, or polished workspace behavior beyond what is needed to establish the platform.

</domain>

<decisions>
## Implementation Decisions

### Workspace structure

- **D-01:** Use a split app architecture with a `Next.js` frontend and a `FastAPI` backend.
- **D-02:** Treat this as a greenfield project and establish stable boundaries early: app surfaces should separate UI, orchestration, persistence, and shared contracts.
- **D-03:** Keep the repo GSD-native from the start, with `.planning/` artifacts committed and phase work flowing through discuss -> plan -> execute -> verify.

### Orchestration contract

- **D-04:** Top-level agent stages must use strict typed inputs/outputs with validator gates before session state can advance.
- **D-05:** A session should auto-run until the next interrupt, approval gate, or completion.
- **D-06:** Helper agents may exist behind a stage boundary, but stage outputs must still conform to the same contract surface.

### Auth and data foundation

- **D-07:** Use `Clerk` for MVP authentication because the first user shape is individual candidates.
- **D-08:** Use `Postgres` as the source of truth for users, sessions, artifacts, approvals, and trace events.
- **D-09:** Reserve `ChromaDB` for semantic retrieval use cases, but do not let it define the primary application data model in this phase.
- **D-10:** All phase-one persistence should assume strict per-user ownership boundaries.

### Observability baseline

- **D-11:** Traceability is a first-class product requirement, not an afterthought; phase one must establish event and artifact persistence that later UI can expose.
- **D-12:** Session artifacts should be modeled in a way that supports later approvals, diffs, scorecards, and reruns.

### Phase workflow

- **D-13:** Each phase must start with a full skill audit over relevant GSD and non-GSD skills, with used/skipped/deferred skills recorded.
- **D-14:** Commits should be intentional and frequent; the user wants each meaningful step committed.

### the agent's Discretion

- Exact package versions
- Local service bootstrapping approach (`uv`, `pnpm`, Docker, etc.)
- Schema/migration tooling choice
- Internal naming conventions once concrete code structure exists

</decisions>

<specifics>
## Specific Ideas

- The product should feel like an instrumented agent system, not a black-box resume chatbot.
- The current product split should lean toward `apps/web`, `apps/api`, and shared schema/contracts so later phases do not need to untangle a monolith.
- Browser/CLI web search may be used by research-capable agents later, but only with citations and validator gates.
- This phase should produce the shell that later supports inline approvals, research summaries, and evaluator traces, even if those surfaces are not fully implemented yet.

</specifics>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project scope

- `.planning/PROJECT.md` — Product framing, core value, constraints, and locked high-level decisions
- `.planning/REQUIREMENTS.md` — v1 requirement set and traceability
- `.planning/ROADMAP.md` — Phase boundary, dependencies, and initial plan slots
- `.planning/STATE.md` — Current focus and project state digest

### Bootstrap research

- `.planning/research/SUMMARY.md` — Roadmap implications and high-level stack/architecture findings
- `.planning/research/STACK.md` — Chosen platform direction and alternatives
- `.planning/research/ARCHITECTURE.md` — Recommended component boundaries and data flow
- `.planning/research/PITFALLS.md` — Failure modes this phase should help prevent

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- No application code exists yet; this phase establishes the reusable assets future phases depend on.

### Established Patterns

- The only existing pattern is the GSD planning scaffold itself; code structure and repo conventions must be created in this phase.

### Integration Points

- Frontend auth/session shell ↔ backend session/orchestration APIs
- Backend persistence layer ↔ Postgres
- Future semantic retrieval boundary ↔ ChromaDB service layer

</code_context>

<deferred>
## Deferred Ideas

- Team coaching, reviewer workflows, and enterprise auth/authorization — separate future scope
- Rich document editor mode beyond the chat-first workspace — deferred until after MVP validation
- Broad export formats beyond markdown — later phase or later milestone

</deferred>

---

_Phase: 01-foundations_
_Context gathered: 2026-04-05_
