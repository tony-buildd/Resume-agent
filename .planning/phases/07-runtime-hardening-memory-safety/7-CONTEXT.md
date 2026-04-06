# Phase 7 Context

## User Goal

Implement the first hardening phase of the approved roadmap:

- add memory tiers and safety metadata
- add interruption intents and delta replanning
- add feasibility and quarantine enforcement
- keep the current product flow stable while doing it

## Constraints

- Continue the GSD lifecycle rather than doing ad hoc refactors.
- Commit and push every small step.
- Keep existing top-level stage names where possible.
- Do not let suspicious or low-confidence evidence reach drafting.

## Source Findings

- The current runtime has only one generic revision loop and no explicit interruption intent model.
- The vault stores provenance and review state, but not independent safety or contamination metadata.
- Draft-safe retrieval is currently modeled mostly through review state and `draft_eligible`.
- The paper review identified memory contamination, interruption handling, and feasibility gating as the highest-leverage backend gaps.
