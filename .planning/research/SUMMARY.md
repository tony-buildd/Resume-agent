# Project Research Summary

**Project:** Resume Agent
**Domain:** Agentic resume optimization platform
**Researched:** 2026-04-05
**Confidence:** MEDIUM

## Executive Summary

Resume Agent behaves more like an agentic strategy workspace than a generic resume rewriter. The research direction captured here supports a product that separates durable memory from final output, keeps orchestration visible, and uses job/company research to shape resume direction rather than only clean up wording.

The recommended implementation path is a `Next.js` workspace over a `FastAPI + LangGraph` backend with `Postgres` as the source of truth and `ChromaDB` as supporting semantic retrieval. The biggest risks are building a shallow vault, hiding orchestration in a black box, and allowing unsupported inferred claims to slip into drafting. The roadmap should therefore start with foundations and observability, then memory, then orchestration, then UI polish.

## Key Findings

### Recommended Stack

The stack should favor a clean split between a modern web UI and a Python agent harness. `Next.js` fits the workspace UX, `FastAPI` fits the service boundary, and `LangGraph` fits the typed stage model. `Postgres + ChromaDB` is the correct pairing because the app needs explicit provenance and approvals, not only semantic recall.

**Core technologies:**
- `Next.js`: workspace UI and artifact presentation — strong fit for a multi-panel chat-first product
- `FastAPI`: backend APIs and persistence — clear and productive for Python services
- `LangGraph`: stage orchestration — aligns with strict contracts and rerun logic
- `Postgres`: durable app state — required for facts, artifacts, approvals, and trace events
- `ChromaDB`: semantic retrieval — useful only as a supporting layer

### Expected Features

The product needs authenticated sessions, a persistent career vault, structured JD analysis, cited research, approval-gated blueprinting, draft generation, evaluator scorecards, and targeted revisions. The differentiators are many-bullets-per-experience memory, visible orchestration, and trust-preserving human checkpoints.

**Must have (table stakes):**
- persistent user auth and private workspace
- JD-driven resume generation
- durable user memory / vault

**Should have (competitive):**
- cited research with strategic impact summary
- evaluator-guided targeted revisions
- inspectable traces and diffs

**Defer (v2+):**
- collaboration workflows
- enterprise auth models
- broader export/editor modes

### Architecture Approach

The major components are the workspace UI, session/orchestration backend, vault/persistence layer, research layer, and evaluator. The architecture should preserve stage contracts and make artifacts first-class so later UI and evaluation work can build on stable interfaces.

**Major components:**
1. Workspace UI — chat, artifact panels, inline approvals, diffs, traces
2. Orchestration backend — session graph, stage transitions, validators, reruns
3. Career vault — facts, provenance, stories, candidate bullets, retrieval rules
4. Research + evaluator services — external evidence and draft scoring

### Critical Pitfalls

1. **Treating the vault like a final resume** — keep many facts and bullets, not just a polished subset
2. **Opaque orchestration** — expose summaries, artifacts, approvals, and score rationale
3. **Over-questioning** — optimize for highest-impact gaps and stop when marginal value drops
4. **Unsupported claims in drafts** — keep inference and approved facts clearly separated

## Implications for Roadmap

Based on the bootstrap research, suggested phase structure:

### Phase 1: Foundations
**Rationale:** The product needs auth, persistence, contracts, and event/trace scaffolding before higher-level agent behavior matters.
**Delivers:** Repo/app skeleton, auth, persistence, orchestration shell, trace/event model
**Addresses:** core trust and architecture requirements
**Avoids:** black-box orchestration and fragile session state

### Phase 2: Career Vault
**Rationale:** Resume quality depends on memory quality, and the vault is the product moat.
**Delivers:** hierarchical memory, provenance states, many bullet candidates per experience
**Uses:** Postgres + ChromaDB split correctly
**Implements:** durable memory component

### Phase 3: Resume Session Flow
**Rationale:** Once memory exists, the orchestration can retrieve, question, strategize, draft, and evaluate.
**Delivers:** JD analysis, research, interrogation, blueprint, draft, evaluator loop
**Implements:** session orchestration component

### Phase 4: Frontend Experience
**Rationale:** The backend flow should exist before polishing how users inspect and act on artifacts.
**Delivers:** chat-centered workspace, contextual panels, diffs, trace summaries

### Phase 5: Ship / Polish
**Rationale:** After the product loop exists, operational fit and documentation become meaningful.
**Delivers:** onboarding, deployment scaffolding, release readiness

### Phase Ordering Rationale

- Foundations first prevents later rework around auth, state, and orchestration contracts.
- Memory before drafting avoids building a fancy interface on top of weak context.
- UI polish after session flow keeps the artifact model grounded in real behavior.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** exact stack versions, auth/storage integration, local dev setup
- **Phase 3:** search source policy, citation UX, evaluator and revision heuristics
- **Phase 4:** interaction quality, accessibility, and artifact presentation patterns

Phases with standard patterns (lighter research burden):
- **Phase 2:** the main complexity is product modeling, not obscure external integration
- **Phase 5:** mostly operational/documentation hardening

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Product direction is clear; exact versions still need validation |
| Features | HIGH | User intent and feature priorities are well defined |
| Architecture | MEDIUM | Strong direction, but implementation details still need Phase 1 planning |
| Pitfalls | HIGH | The main failure modes are already explicit from the user problem statement |

**Overall confidence:** MEDIUM

### Gaps to Address

- Validate exact package/runtime versions during Phase 1 planning
- Refine external research source policy during Phase 3 planning
- Refine UI motion/accessibility expectations during Phase 4 planning

## Sources

### Primary (HIGH confidence)
- Bootstrap product discussion and locked project decisions
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`

### Secondary (MEDIUM confidence)
- GSD workflow assumptions and project operating model

### Tertiary (LOW confidence)
- Specific library/version details deferred for validation during phase planning

---
*Research completed: 2026-04-05*
*Ready for roadmap: yes*
