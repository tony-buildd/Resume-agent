# Phase 5: Ship / Polish - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Finish the MVP by making it understandable and runnable for another developer, and by documenting how this repo should be operated going forward. This phase covers local setup, environment guidance, onboarding, deployment/release notes, and the GSD-native working model. It does not add major new product features.

</domain>

<decisions>
## Implementation Decisions

### Documentation
- **D-01:** The repo needs explicit local setup docs beyond the current short README snippets.
- **D-02:** Environment guidance should be centralized so developers know which keys are required, where they come from, and what is optional.
- **D-03:** Developer onboarding should explain both the product architecture and the everyday commands needed to work in the repo.

### Deployment / release readiness
- **D-04:** Phase 5 should document a practical deployment strategy even if the repo is not fully auto-deployed yet.
- **D-05:** Release guidance should separate `web`, `api`, `database`, and secrets responsibilities clearly.
- **D-06:** The repo should document a release checklist that matches the GSD workflow already used in development.

### Operating model
- **D-07:** The GSD-native workflow should be documented as the default way to evolve the project.
- **D-08:** Operational docs should point back to `.planning/` as the canonical project OS.
- **D-09:** The final docs should optimize for handoff: a new developer should be able to understand the system and keep it moving without reverse engineering prior sessions.

### the agent's Discretion
- Exact docs folder structure
- Whether deployment guidance is platform-specific or intentionally generic for the first pass
- How much release process detail belongs in README versus deeper docs

</decisions>

<specifics>
## Specific Ideas

- The README should stay product-first; onboarding and ops detail should live in docs.
- The final milestone should make this repo feel maintained, not just built.
- The docs should explain the difference between canonical product artifacts, code, and GSD workflow artifacts.

</specifics>

<canonical_refs>
## Canonical References

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/04-frontend-experience/04-UAT.md`
- `README.md`
- `package.json`
- `apps/api/pyproject.toml`
- `.env.example`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `README.md` now describes the product thesis clearly.
- `.env.example` already lists the main required environment variables.
- `package.json` already exposes the main dev/build commands for the web and API apps.
- `apps/api/README.md` exists as an API-local anchor for backend-specific guidance if needed.

### Current Gaps
- There is no proper local onboarding document.
- There is no deployment or release checklist.
- There is no single operating guide for how GSD is used in this repo.
- There is no explicit “how to run the full stack” doc for a new developer.

</code_context>

<deferred>
## Deferred Ideas

- CI automation and release pipelines can be expanded later if needed.
- Multi-environment deployment automation can wait until a hosting target is locked.

</deferred>

---

*Phase: 05-ship-polish*
*Context gathered: 2026-04-05*
