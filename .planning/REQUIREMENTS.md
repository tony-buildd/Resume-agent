# Requirements: Resume Agent

**Defined:** 2026-04-05
**Core Value:** Turn fragmented career context into a credible, strategically tailored one-page resume that matches a target role without hiding how the system reached its recommendations.

## v1 Requirements

### Authentication

- [ ] **AUTH-01**: User can sign in and sign up with Clerk-backed authentication.
- [ ] **AUTH-02**: Authenticated users can access only their own career vault, sessions, and generated artifacts.
- [ ] **AUTH-03**: User session persists across refresh and returning visits.

### Career Vault

- [ ] **VAULT-01**: User can seed the career vault from existing materials such as a resume, portfolio, or profile links.
- [ ] **VAULT-02**: User can build the vault through an agent-led interview that stays within one role or project thread at a time.
- [ ] **VAULT-03**: The system stores hierarchical career memory as company -> role -> project story -> claim/evidence facts.
- [ ] **VAULT-04**: Every stored fact shows provenance and review state (`user_stated`, `inferred`, `approved`, `rejected`).
- [ ] **VAULT-05**: One experience can retain many candidate bullets linked to shared facts and story-specific facts.
- [ ] **VAULT-06**: Unapproved inferred facts can support future questioning but cannot be used in drafting.

### Research

- [ ] **RSCH-01**: User can submit a job description and receive structured JD analysis with requirements, archetype, and success signals.
- [ ] **RSCH-02**: The system can research company and role context with cited sources.
- [ ] **RSCH-03**: Research results show a concise strategic summary explaining how findings affect resume direction.

### Session Flow

- [ ] **FLOW-01**: A tailoring session auto-runs until the next interrupt, approval gate, or completion.
- [ ] **FLOW-02**: The Interrogator asks one highest-impact question at a time and explains why it matters.
- [ ] **FLOW-03**: User must approve JD analysis before the system can lock the resume strategy.
- [ ] **FLOW-04**: User must approve the narrative blueprint before draft generation starts.
- [ ] **FLOW-05**: User edits become the canonical session state for downstream stages.
- [ ] **FLOW-06**: Revision requests rerun from the earliest affected stage instead of restarting the entire session.

### Resume Drafting

- [ ] **WRIT-01**: The system generates a one-page markdown resume tailored to the target role.
- [ ] **WRIT-02**: The final package includes the resume, an evaluator scorecard, and interview talking points / concern handling notes.
- [ ] **WRIT-03**: Every full draft is scored for fit, evidence support, specificity, and overstatement risk.
- [ ] **WRIT-04**: Evaluator-driven revisions are targeted to the weak sections rather than full redrafts by default.

### Workspace UX

- [ ] **UX-01**: The desktop workspace is chat-centered with contextual side panels for JD analysis, vault context, blueprint, draft, and traces.
- [ ] **UX-02**: Candidate facts, blueprint items, and revision suggestions support inline `accept`, `edit`, and `reject`.
- [ ] **UX-03**: Revised bullets and draft sections are shown with inline diffs and short rationale.

### Observability

- [ ] **OBS-01**: The product shows stage traces as summaries by default with expandable detail.
- [ ] **OBS-02**: The system stores stage events, artifacts, approvals, and scorecards for each session.

### Operations

- [ ] **OPS-01**: Developers can bootstrap the full local stack from repo documentation and tracked configuration.
- [ ] **OPS-02**: The project has deployment-ready environment and release scaffolding for the web app and backend.
- [ ] **OPS-03**: The repo documents the GSD-native workflow and expected project operating model.

### Agent Capability Integration

- [ ] **CAP-01**: Codex can discover repo-local skills that wrap external capability sources relevant to this project.
- [ ] **CAP-02**: The repo provides a reproducible bootstrap path for Codex-compatible external skills and tools without requiring ad hoc manual copying.
- [ ] **CAP-03**: Browser Use guidance is available as a Codex-native skill with the project's preferred conventions (`uv`, Pydantic v2, pre-commit, ChatBrowserUse default).
- [ ] **CAP-04**: Hermes availability is documented and smoke-tested so the local CLI can be used intentionally rather than implicitly.
- [ ] **CAP-05**: Paper-to-code workflows are exposed through a Codex-native skill or helper surface instead of remaining an unstructured external repo link.

### Runtime Hardening and Memory Safety

- [ ] **SAFE-01**: Vault records and session flow can distinguish memory tiers (`canonical`, `progress`, `feasibility`, `quarantine`) from user review state.
- [ ] **SAFE-02**: Vault records persist validation status, contamination risk, quarantine reason, and feasibility checks independently from provenance.
- [ ] **SAFE-03**: Session runtime accepts explicit interruption intents (`add_requirement`, `revise_requirement`, `retract_requirement`, `clarify_fact`, `risk_flag`).
- [ ] **SAFE-04**: Replanning targets the earliest affected stage instead of using one generic rerun path.
- [ ] **SAFE-05**: Quarantined or failed-feasibility evidence can support questioning but cannot become draft-safe input.

### Retrieval and Context Budgeting

- [ ] **RETR-01**: Retrieval shortlists roles, then stories, then supporting evidence instead of ranking only whole roles.
- [ ] **RETR-02**: Session context assembly respects token budgets for JD constraints, canonical context, selected evidence, and current user answers.
- [ ] **RETR-03**: Blueprint selection uses configurable evidence budgets rather than only fixed small hard caps.
- [ ] **RETR-04**: Retrieval artifacts explain what was selected, omitted, or compressed and why.

### Adaptive Evaluation

- [ ] **EVAL-01**: The evaluator generates a role-aware rubric rather than using a fixed keyword scorecard.
- [ ] **EVAL-02**: Evaluation includes trajectory judgments about question quality, action efficiency, and rerun targeting.
- [ ] **EVAL-03**: Every evaluation dimension stores explicit evidence so the user can inspect score changes.
- [ ] **EVAL-04**: Saved sessions can be replayed through offline evaluation fixtures for product QA.

### Capability Routing and Research Orchestration

- [ ] **ROUTE-01**: Research and tool use is driven by an explicit capability registry with scope, trust, latency, auth, and structured-output metadata.
- [ ] **ROUTE-02**: Research execution prefers internal data, then API/MCP sources, then structured external sources, and only then browser fallback.
- [ ] **ROUTE-03**: Research stages emit `research-plan`, `source-bundle`, `strategy-synthesis`, and `capability-route` artifacts.
- [ ] **ROUTE-04**: Browser Use, Hugging Face papers, Hermes, and Paper2Code each have explicit usage boundaries inside the runtime.

### Progressive UX Control Surfaces

- [ ] **UX-04**: The workspace progressively reveals micro-interventions, sidecar review, or full inspection surfaces based on task complexity.
- [ ] **UX-05**: Users can trigger interruption intents and narrative scope changes directly from the workspace.
- [ ] **UX-06**: Users can inspect evidence selection, compression, quarantine/risk state, capability route, and evaluator dimension details in the UI.

## v2 Requirements

### Collaboration

- **COLL-01**: User can manage multiple resume variants and saved application packets per target company.
- **COLL-02**: Coaches or collaborators can review artifacts with scoped permissions.

### Editing

- **EDIT-01**: User can switch between guided chat mode and a richer document editor mode.
- **EDIT-02**: The system can export to multiple resume formats beyond markdown.

## Out of Scope

| Feature                                                        | Reason                                                    |
| -------------------------------------------------------------- | --------------------------------------------------------- |
| Enterprise SSO and org RBAC                                    | Not needed for individual-user MVP                        |
| Native mobile clients                                          | Web-first scope is sufficient for learning and validation |
| Fully autonomous, uncited market research hidden from the user | The product needs visible trust and traceability          |
| Silent fabrication of unsupported claims                       | Conflicts with the chosen suggest-and-confirm trust model |

## Traceability

| Requirement | Phase   | Status  |
| ----------- | ------- | ------- |
| AUTH-01     | Phase 1 | Pending |
| AUTH-02     | Phase 1 | Pending |
| AUTH-03     | Phase 1 | Pending |
| VAULT-01    | Phase 2 | Pending |
| VAULT-02    | Phase 2 | Pending |
| VAULT-03    | Phase 2 | Pending |
| VAULT-04    | Phase 2 | Pending |
| VAULT-05    | Phase 2 | Pending |
| VAULT-06    | Phase 2 | Pending |
| RSCH-01     | Phase 3 | Pending |
| RSCH-02     | Phase 3 | Pending |
| RSCH-03     | Phase 3 | Pending |
| FLOW-01     | Phase 1 | Pending |
| FLOW-02     | Phase 3 | Pending |
| FLOW-03     | Phase 3 | Pending |
| FLOW-04     | Phase 3 | Pending |
| FLOW-05     | Phase 3 | Pending |
| FLOW-06     | Phase 3 | Pending |
| WRIT-01     | Phase 3 | Pending |
| WRIT-02     | Phase 3 | Pending |
| WRIT-03     | Phase 3 | Pending |
| WRIT-04     | Phase 3 | Pending |
| UX-01       | Phase 4 | Pending |
| UX-02       | Phase 4 | Pending |
| UX-03       | Phase 4 | Pending |
| OBS-01      | Phase 4 | Pending |
| OBS-02      | Phase 1 | Pending |
| OPS-01      | Phase 5 | Pending |
| OPS-02      | Phase 5 | Pending |
| OPS-03      | Phase 5 | Pending |
| CAP-01      | Phase 6 | Pending |
| CAP-02      | Phase 6 | Pending |
| CAP-03      | Phase 6 | Pending |
| CAP-04      | Phase 6 | Pending |
| CAP-05      | Phase 6 | Pending |
| SAFE-01     | Phase 7 | Pending |
| SAFE-02     | Phase 7 | Pending |
| SAFE-03     | Phase 7 | Pending |
| SAFE-04     | Phase 7 | Pending |
| SAFE-05     | Phase 7 | Pending |
| RETR-01     | Phase 8 | Pending |
| RETR-02     | Phase 8 | Pending |
| RETR-03     | Phase 8 | Pending |
| RETR-04     | Phase 8 | Pending |
| EVAL-01     | Phase 9 | Pending |
| EVAL-02     | Phase 9 | Pending |
| EVAL-03     | Phase 9 | Pending |
| EVAL-04     | Phase 9 | Pending |
| ROUTE-01    | Phase 10 | Pending |
| ROUTE-02    | Phase 10 | Pending |
| ROUTE-03    | Phase 10 | Pending |
| ROUTE-04    | Phase 10 | Pending |
| UX-04       | Phase 11 | Pending |
| UX-05       | Phase 11 | Pending |
| UX-06       | Phase 11 | Pending |

**Coverage:**

- v1 requirements: 55 total
- Mapped to phases: 55
- Unmapped: 0 ✓

---

_Requirements defined: 2026-04-05_
_Last updated: 2026-04-05 after adding hardening and evolution requirements_
