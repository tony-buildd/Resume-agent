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

## v2 Requirements

### Collaboration

- **COLL-01**: User can manage multiple resume variants and saved application packets per target company.
- **COLL-02**: Coaches or collaborators can review artifacts with scoped permissions.

### Editing

- **EDIT-01**: User can switch between guided chat mode and a richer document editor mode.
- **EDIT-02**: The system can export to multiple resume formats beyond markdown.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Enterprise SSO and org RBAC | Not needed for individual-user MVP |
| Native mobile clients | Web-first scope is sufficient for learning and validation |
| Fully autonomous, uncited market research hidden from the user | The product needs visible trust and traceability |
| Silent fabrication of unsupported claims | Conflicts with the chosen suggest-and-confirm trust model |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | Phase 1 | Pending |
| AUTH-02 | Phase 1 | Pending |
| AUTH-03 | Phase 1 | Pending |
| VAULT-01 | Phase 2 | Pending |
| VAULT-02 | Phase 2 | Pending |
| VAULT-03 | Phase 2 | Pending |
| VAULT-04 | Phase 2 | Pending |
| VAULT-05 | Phase 2 | Pending |
| VAULT-06 | Phase 2 | Pending |
| RSCH-01 | Phase 3 | Pending |
| RSCH-02 | Phase 3 | Pending |
| RSCH-03 | Phase 3 | Pending |
| FLOW-01 | Phase 1 | Pending |
| FLOW-02 | Phase 3 | Pending |
| FLOW-03 | Phase 3 | Pending |
| FLOW-04 | Phase 3 | Pending |
| FLOW-05 | Phase 3 | Pending |
| FLOW-06 | Phase 3 | Pending |
| WRIT-01 | Phase 3 | Pending |
| WRIT-02 | Phase 3 | Pending |
| WRIT-03 | Phase 3 | Pending |
| WRIT-04 | Phase 3 | Pending |
| UX-01 | Phase 4 | Pending |
| UX-02 | Phase 4 | Pending |
| UX-03 | Phase 4 | Pending |
| OBS-01 | Phase 4 | Pending |
| OBS-02 | Phase 1 | Pending |
| OPS-01 | Phase 5 | Pending |
| OPS-02 | Phase 5 | Pending |
| OPS-03 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 30 total
- Mapped to phases: 30
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-05*
*Last updated: 2026-04-05 after initial definition*
