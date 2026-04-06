# Roadmap: Resume Agent

## Overview

This roadmap builds Resume Agent from project skeleton to a hardened, inspectable product prototype in eleven phases. The first six phases delivered the working MVP and capability bootstrap layer. The next five phases preserve that working flow while hardening runtime safety, retrieval scaling, evaluation quality, research routing, and progressive UX controls.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Foundations** - Set up the repo, runtime split, auth, data plumbing, orchestration shell, and trace/event model.
- [x] **Phase 2: Career Vault** - Build the persistent memory layer for roles, stories, facts, provenance, and reusable bullet candidates.
- [x] **Phase 3: Resume Session Flow** - Implement JD analysis, research, interrogation, blueprint approval, drafting, and evaluator-driven revision loops.
- [x] **Phase 4: Frontend Experience** - Build the chat-first workspace with contextual panels, inline approvals, diffs, and trace views.
- [x] **Phase 5: Ship / Polish** - Harden operations, documentation, onboarding, and release packaging for a usable MVP.
- [x] **Phase 6: Agent Capability Integration** - Add Codex-native wrappers, bootstrap scripts, and docs for external skill ecosystems and agent tooling.
- [x] **Phase 7: Runtime Hardening and Memory Safety** - Split trust from safety, add interruption intents, delta replanning, and quarantine/feasibility enforcement.
- [x] **Phase 8: Hierarchical Retrieval and Context Budgeting** - Replace flat retrieval with role/story/evidence selection and budget-aware context assembly.
- [x] **Phase 9: Adaptive Evaluation and Review Loop** - Replace the shallow evaluator with role-aware rubrics, trajectory judgments, and replayable QA fixtures.
- [x] **Phase 10: Capability Routing and Research Orchestration** - Add a capability registry, API-first routing policy, and multi-pass research artifacts with citations.
- [ ] **Phase 11: Progressive UX and Control Surfaces** - Expose interruption, evidence, risk, and route controls progressively without overwhelming the workspace.

## Phase Details

### Phase 1: Foundations

**Goal**: Deliver a working monorepo/app skeleton with frontend/backend split, auth, storage foundations, orchestration shell, and session trace/event persistence.
**Depends on**: Nothing (first phase)
**Requirements**: AUTH-01, AUTH-02, AUTH-03, FLOW-01, OBS-02
**Success Criteria** (what must be TRUE):

1. User can authenticate and reach a protected workspace shell.
2. The backend can create and persist a session envelope with stage, artifacts, and event history.
3. The repo is structured so later phases can add the vault, orchestration stages, and UI without reworking the project foundation.
   **Plans**: 3 plans

Plans:

- [x] 01-01: Scaffold the workspace, package structure, local tooling, and shared environment conventions.
- [x] 01-02: Wire Clerk, Postgres, and backend persistence for users, sessions, artifacts, and trace events.
- [x] 01-03: Create the orchestration shell, typed contracts, and skill audit/project workflow docs.

### Phase 2: Career Vault

**Goal**: Build the structured career memory system that can grow over time and feed multiple resume narratives from the same experience.
**Depends on**: Phase 1
**Requirements**: VAULT-01, VAULT-02, VAULT-03, VAULT-04, VAULT-05, VAULT-06
**Success Criteria** (what must be TRUE):

1. User can seed the vault from imported materials and continue enriching it through guided interview threads.
2. The system stores company, role, project story, claim/evidence facts, and many candidate bullets with provenance.
3. Drafting-safe retrieval excludes unapproved inferred facts while questioning can still use dormant inference candidates.
   **Plans**: 3 plans

Plans:

- [x] 02-01: Design and implement vault schema, provenance states, and bullet candidate storage.
- [x] 02-02: Build import + interview-first ingestion flows and story checkpoint review behavior.
- [x] 02-03: Add retrieval rules for approved, inferred, rejected, and dormant vault items.

### Phase 3: Resume Session Flow

**Goal**: Deliver the core multi-stage tailoring flow from JD intake to final draft package with evaluator-guided revisions.
**Depends on**: Phase 2
**Requirements**: RSCH-01, RSCH-02, RSCH-03, FLOW-02, FLOW-03, FLOW-04, FLOW-05, FLOW-06, WRIT-01, WRIT-02, WRIT-03, WRIT-04
**Success Criteria** (what must be TRUE):

1. User can submit a JD and receive structured JD analysis plus cited company/role research.
2. The system asks one highest-impact question at a time, pauses at approval gates, and persists canonical user edits.
3. The system generates a one-page markdown resume, scorecard, and interview notes, then can rerun targeted revisions from the earliest affected stage.
   **Plans**: 4 plans

Plans:

- [x] 03-01: Implement JD analysis and research stages with citation-aware outputs.
- [x] 03-02: Implement interrogation, approval gates, and canonical artifact editing behavior.
- [x] 03-03: Implement narrative blueprinting, drafting, and final package assembly.
- [x] 03-04: Implement evaluator scoring and targeted revision reruns.

### Phase 4: Frontend Experience

**Goal**: Make the orchestration legible and usable through a chat-first workspace with contextual artifacts and revision review UI.
**Depends on**: Phase 3
**Requirements**: UX-01, UX-02, UX-03, OBS-01
**Success Criteria** (what must be TRUE):

1. The workspace keeps conversation central while surfacing the right artifact panel for the active stage.
2. User can accept, edit, and reject facts and suggestions inline without losing orchestration state.
3. Revision diffs and trace summaries are visible enough that the system feels inspectable rather than black-box.
   **Plans**: 3 plans

Plans:

- [x] 04-01: Build the chat-centered shell and contextual panel system.
- [x] 04-02: Build inline approval, editing, and artifact diff interactions.
- [x] 04-03: Build trace summary and expanded debug/detail views with strong usability and accessibility.

### Phase 5: Ship / Polish

**Goal**: Make the MVP runnable, deployable, documented, and ready for repeated development through GSD.
**Depends on**: Phase 4
**Requirements**: OPS-01, OPS-02, OPS-03
**Success Criteria** (what must be TRUE):

1. Another developer can clone the repo, follow docs, and run the full stack locally.
2. Deployment/environment scaffolding exists for the frontend and backend with clear secrets/config guidance.
3. The repo documents the GSD-native workflow, release flow, and ongoing development expectations.
   **Plans**: 2 plans

Plans:

- [x] 05-01: Document local setup, env management, and developer onboarding.
- [x] 05-02: Add deployment/release hardening and project operating docs.

### Phase 6: Agent Capability Integration

**Goal**: Make external agent ecosystems and tools usable from this repo through stable Codex-native skills, scripts, and verification docs.
**Depends on**: Phase 5
**Requirements**: CAP-01, CAP-02, CAP-03, CAP-04, CAP-05
**Success Criteria** (what must be TRUE):

1. Repo-local `.agents/skills` includes Codex-usable wrappers or installed skills for the chosen external capability sources.
2. Developers can run one documented bootstrap flow to set up those capabilities and understand what is installed directly vs wrapped locally.
3. Browser Use, Hermes, and Paper2Code each have an intentional entry point in this repo rather than existing as disconnected external references.
   **Plans**: 3 plans

Plans:

- [x] 06-01: Set up the capability bootstrap layer and install/adapt the selected external skill sources for Codex.
- [x] 06-02: Add Codex-native Browser Use, Hermes, and Paper2Code integration surfaces.
- [x] 06-03: Verify the capability stack and document how to use it from this repo.

### Phase 7: Runtime Hardening and Memory Safety

**Goal**: Make the runtime and vault resilient to memory contamination, user interruptions, and unsafe evidence promotion while keeping the existing product flow intact.
**Depends on**: Phase 6
**Requirements**: SAFE-01, SAFE-02, SAFE-03, SAFE-04, SAFE-05
**Success Criteria** (what must be TRUE):

1. Vault records and session envelopes can model memory tier, validation state, contamination risk, quarantine reason, and feasibility checks independently from provenance review state.
2. The runtime can accept explicit interruption intents and reroute from the earliest affected stage instead of a single generic revision loop.
3. Suspicious or low-confidence evidence can support future questioning but cannot drive blueprinting or drafting unless it becomes validated and draft-safe.
   **Plans**: 3 plans

Plans:

- [x] 07-01: Extend vault/session schema, typed contracts, and API payloads for memory tiers, validation state, and interruption summaries.
- [x] 07-02: Implement interruption-aware delta replanning and runtime transition policy.
- [x] 07-03: Implement feasibility/quarantine services, promotion gates, and trace visibility for memory-risk decisions.

### Phase 8: Hierarchical Retrieval and Context Budgeting

**Goal**: Scale the career vault and session context by retrieving evidence hierarchically and assembling stage inputs under explicit context budgets.
**Depends on**: Phase 7
**Requirements**: RETR-01, RETR-02, RETR-03, RETR-04
**Success Criteria** (what must be TRUE):

1. Retrieval first narrows roles, then stories, then evidence, instead of flattening everything into whole-role lexical ranking.
2. Stage context budgets preserve JD constraints, canonical user context, and high-signal evidence while compressing low-value history when needed.
3. Blueprint and retrieval artifacts explain why evidence was selected, omitted, or compressed and honor configurable evidence budgets.
   **Plans**: 3 plans

Plans:

- [x] 08-01: Implement hierarchical role/story/evidence retrieval and scoring traces.
- [x] 08-02: Implement a context budget manager with budget slices and compression summaries.
- [x] 08-03: Move blueprint selection to configurable evidence budgets and expose retrieval/compression artifacts.

### Phase 9: Adaptive Evaluation and Review Loop

**Goal**: Replace the prototype scorecard with a rubric engine that grades both output quality and orchestration process quality.
**Depends on**: Phase 8
**Requirements**: EVAL-01, EVAL-02, EVAL-03, EVAL-04
**Success Criteria** (what must be TRUE):

1. Evaluation adapts to role archetype and session context instead of using a single fixed rubric.
2. The system scores trajectory quality, including question choice, action efficiency, and rerun targeting, alongside final draft quality.
3. Evaluation evidence is persisted and replayable so saved sessions can be audited offline for product QA.
   **Plans**: 3 plans

Plans:

- [x] 09-01: Implement rubric generation, dimension weighting, and the new scorecard types.
- [x] 09-02: Implement trajectory-aware evaluation, rerun recommendations, and evaluator evidence persistence.
- [x] 09-03: Add offline replay fixtures and QA-oriented evaluation commands.

### Phase 10: Capability Routing and Research Orchestration

**Goal**: Make research and tool use intentional by routing through a capability registry and multi-pass research planner before browser fallback.
**Depends on**: Phase 9
**Requirements**: ROUTE-01, ROUTE-02, ROUTE-03, ROUTE-04
**Success Criteria** (what must be TRUE):

1. Research and tool use choices are explained through a capability registry and route trace rather than hidden heuristics.
2. Research runs through planned subquestions, source collection, and synthesis artifacts with citations and confidence.
3. Browser Use, Hugging Face papers, Hermes, and Paper2Code are each used only in their intended boundary within the system.
   **Plans**: 3 plans

Plans:

- [x] 10-01: Implement the capability registry and route metadata surface.
- [x] 10-02: Refactor research into plan -> source bundle -> synthesis artifacts with capability-aware execution.
- [x] 10-03: Add route traces and the paper-to-design helper flow for architecture research.

### Phase 11: Progressive UX and Control Surfaces

**Goal**: Surface the new runtime, evidence, and routing controls in a way that stays chat-first and readable.
**Depends on**: Phase 10
**Requirements**: UX-04, UX-05, UX-06
**Success Criteria** (what must be TRUE):

1. The workspace progressively reveals the right control surface for simple edits, active replanning, or full inspection.
2. Users can trigger interruption intents, adjust narrative scope, and inspect evidence/risk decisions without losing session context.
3. Evaluator drilldowns and capability-route panels are visible when needed without overwhelming the default workspace.
   **Plans**: 3 plans

Plans:

- [ ] 11-01: Implement progressive workspace states and sidecar/full-surface transitions.
- [ ] 11-02: Add interruption controls, narrative scope controls, and evidence risk panels.
- [ ] 11-03: Add evaluator drilldowns and capability-route visibility throughout the workspace.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11

| Phase                  | Plans Complete | Status      | Completed  |
| ---------------------- | -------------- | ----------- | ---------- |
| 1. Foundations         | 3/3            | Complete    | 2026-04-05 |
| 2. Career Vault        | 3/3            | Complete    | 2026-04-06 |
| 3. Resume Session Flow | 4/4            | Complete    | 2026-04-05 |
| 4. Frontend Experience | 3/3            | Complete    | 2026-04-05 |
| 5. Ship / Polish       | 2/2            | Complete    | 2026-04-05 |
| 6. Agent Capability Integration | 3/3     | Complete    | 2026-04-05 |
| 7. Runtime Hardening and Memory Safety | 3/3 | Complete | 2026-04-05 |
| 8. Hierarchical Retrieval and Context Budgeting | 0/3 | Not Started | — |
| 9. Adaptive Evaluation and Review Loop | 0/3 | Not Started | — |
| 10. Capability Routing and Research Orchestration | 0/3 | Not Started | — |
| 11. Progressive UX and Control Surfaces | 0/3 | Not Started | — |
