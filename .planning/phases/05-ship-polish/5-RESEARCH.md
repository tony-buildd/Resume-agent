# Phase 5: Ship / Polish - Research

## Current Repo Readiness

The product itself is in solid MVP shape, but the repository still reads like an active build site rather than a handoff-ready project. The missing layer is operational clarity: how to set it up, how to run it, how to think about environments, and how to continue work in the same structured way.

## Recommended Documentation Split

### 1. Developer onboarding
- Local setup
- required tools
- dependency install
- env setup
- first-run commands
- expected ports and services

### 2. Deployment guidance
- what is deployed
- where secrets live
- current recommended hosting strategy
- database expectations
- release checklist before shipping

### 3. Project operating guide
- how `.planning/` is used
- how GSD phases are expected to run
- how summaries/UAT/state updates are kept in sync
- what “small commits + push every step” means in practice

## Recommended Implementation Direction

Keep the root README product-focused and move implementation/onboarding detail into `docs/`. That preserves the project story for outsiders while giving contributors the depth they actually need.

## Risks

- If setup guidance stays fragmented between README, env files, and phase artifacts, onboarding remains slow.
- If deployment guidance is too abstract, the final phase will not really satisfy `OPS-02`.
- If the GSD operating model is undocumented, future contributors will drift back into ad hoc workflow.

## Suggested Final Slice Order

1. Add local setup, env, and onboarding docs.
2. Add deployment and release docs.
3. Add project operating/GSD workflow docs.
4. Close the phase with a final UAT/report.

---

*Phase: 05-ship-polish*
*Research captured: 2026-04-05*
