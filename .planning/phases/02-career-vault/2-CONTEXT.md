# Phase 2: Career Vault - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the structured career memory system that can store durable user context across many resume sessions. This phase covers ingestion, canonical data modeling, provenance/review state, and storage/retrieval boundaries for career facts and candidate bullets. It does not implement the full JD-to-resume orchestration flow or the polished artifact-review UI beyond what the vault needs to persist.

</domain>

<decisions>
## Implementation Decisions

### Vault shape

- **D-01:** The canonical vault hierarchy is `company -> role -> project story -> claim/evidence fact`.
- **D-02:** One role or project can retain many candidate bullets, because different target jobs will need different bullet subsets from the same experience.
- **D-03:** Candidate bullets must stay linked to their underlying facts so later resume generation can explain provenance instead of treating bullets as isolated text.

### Trust and review model

- **D-04:** Every fact stored in the vault must carry provenance and review state, including `user_stated`, `inferred`, `approved`, and `rejected`.
- **D-05:** Unapproved inferred facts may support future questioning and retrieval, but they cannot be used directly in drafting.
- **D-06:** The product should support batch review at story checkpoints instead of forcing the user to approve every micro-fact immediately.

### Ingestion flow

- **D-07:** Vault ingestion is interview-first, but the user can seed it from existing materials such as a resume, portfolio, or profile links.
- **D-08:** The agent should stay within one role or project thread at a time until ownership, stack, architecture, and impact are clear.
- **D-09:** The vault should become useful before the user has completed their whole career history; one strong captured role is enough to support future session work.

### Storage and retrieval boundaries

- **D-10:** `Postgres` remains the source of truth for canonical career entities, bullets, provenance, and review state.
- **D-11:** `ChromaDB` should only index long-form notes, prior answers, and other fuzzy retrieval material; it must not become the primary record of the user's career.
- **D-12:** Retrieval should be aware of fact state, so approved facts and draft-eligible bullets are distinguishable from questioning-only inferred material.

### Resume-optimization behavior

- **D-13:** The vault must preserve the maximum useful detail per experience, not prematurely compress each role down to a one-page resume shape.
- **D-14:** The product should optimize later role-specific selection by storing alternate stories, alternate bullets, and missing-info prompts for the same experience.

### the agent's Discretion

- Exact table/schema naming
- Ingestion endpoint boundaries and service-layer organization
- Embedding model choice and Chroma collection structure
- Whether review checkpoints are represented as dedicated artifacts or vault-specific states

</decisions>

<specifics>
## Specific Ideas

- A single experience may contain many possible bullets and story angles; the vault exists so the system can choose the right subset per target role later.
- The interview pattern should feel like a focused technical debrief, not a polished resume rewrite, so the system can recover forgotten architecture details and metrics over time.
- The system should preserve both “safe factual memory” and “aggressive inferred framing,” but those need explicit review separation.

</specifics>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product and requirement scope

- `.planning/PROJECT.md` — Product framing, trust model, and locked stack decisions
- `.planning/REQUIREMENTS.md` — Vault requirements `VAULT-01` through `VAULT-06`
- `.planning/ROADMAP.md` — Phase boundary and dependency on Foundations
- `.planning/STATE.md` — Current workflow state

### Prior phase foundation

- `.planning/phases/01-foundations/1-CONTEXT.md` — Foundation decisions that constrain phase boundaries
- `.planning/phases/01-foundations/01-02-SUMMARY.md` — Auth and persistence foundation built in Phase 1
- `.planning/phases/01-foundations/01-03-SUMMARY.md` — Typed session/runtime shell built in Phase 1
- `docs/architecture/foundation-contracts.md` — Session, artifact, trace, and auth contracts that Phase 2 should extend

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `apps/api/app/db/models.py` - Existing user/session/artifact/trace foundation that Phase 2 can extend with vault entities
- `apps/api/app/orchestration/contracts.py` - Typed session/artifact envelope patterns worth mirroring for vault APIs
- `apps/api/app/orchestration/runtime.py` - Deterministic runtime shell that later vault ingestion stages can plug into
- `apps/web/src/lib/api/sessions.ts` - Existing server-side API client pattern for authenticated web-to-API calls

### Established Patterns

- Phase 1 established `Postgres` as the canonical source of truth and `ChromaDB` as secondary semantic infrastructure
- Session state, artifacts, and traces are explicit typed contracts rather than ad hoc JSON blobs
- Protected user scope is anchored to one canonical `AppUser` identity

### Integration Points

- Vault ingestion should attach to the existing session/orchestration shell rather than bypass it
- Vault persistence must remain user-scoped and compatible with current API auth boundaries
- Candidate bullets and fact-review artifacts should be renderable through the artifact/trace model introduced in Phase 1

</code_context>

<deferred>
## Deferred Ideas

- Rich visual vault exploration tools and editorial diff UX belong primarily to Phase 4
- Full JD analysis and research-driven resume strategy stay in Phase 3
- Collaboration, sharing, and coach review workflows remain out of MVP scope

</deferred>

---

_Phase: 02-career-vault_
_Context gathered: 2026-04-05_
