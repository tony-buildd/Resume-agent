# Roadmap: Resume Agent

## Overview

This roadmap builds Resume Agent from project skeleton to a production-ready MVP in five phases. The flow intentionally mirrors the product philosophy: establish trustworthy foundations and observability first, build durable career memory second, layer in JD-driven orchestration third, craft the visible workspace fourth, and finish with polish, onboarding, and release readiness.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Foundations** - Set up the repo, runtime split, auth, data plumbing, orchestration shell, and trace/event model.
- [x] **Phase 2: Career Vault** - Build the persistent memory layer for roles, stories, facts, provenance, and reusable bullet candidates.
- [x] **Phase 3: Resume Session Flow** - Implement JD analysis, research, interrogation, blueprint approval, drafting, and evaluator-driven revision loops.
- [x] **Phase 4: Frontend Experience** - Build the chat-first workspace with contextual panels, inline approvals, diffs, and trace views.
- [x] **Phase 5: Ship / Polish** - Harden operations, documentation, onboarding, and release packaging for a usable MVP.
- [ ] **Phase 6: Agent Capability Integration** - Add Codex-native wrappers, bootstrap scripts, and docs for external skill ecosystems and agent tooling.

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

- [ ] 06-01: Set up the capability bootstrap layer and install/adapt the selected external skill sources for Codex.
- [ ] 06-02: Add Codex-native Browser Use, Hermes, and Paper2Code integration surfaces.
- [ ] 06-03: Verify the capability stack and document how to use it from this repo.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase                  | Plans Complete | Status      | Completed  |
| ---------------------- | -------------- | ----------- | ---------- |
| 1. Foundations         | 3/3            | Complete    | 2026-04-05 |
| 2. Career Vault        | 3/3            | Complete    | 2026-04-06 |
| 3. Resume Session Flow | 4/4            | Complete    | 2026-04-05 |
| 4. Frontend Experience | 3/3            | Complete    | 2026-04-05 |
| 5. Ship / Polish       | 2/2            | Complete    | 2026-04-05 |
| 6. Agent Capability Integration | 0/3     | Not Started | —          |
