# Phase 4: Frontend Experience - Research

## Current UI Reality

The existing workspace is useful as a runtime inspector but not yet as a product UI. It renders stage state, vault summaries, artifacts, and trace events, but everything is stacked into a mostly diagnostic layout. The next phase should preserve that inspectability while reorganizing the page around the actual user workflow: conversation first, active artifact second, deep trace context third.

## Recommended Frontend Direction

### 1. Server shell + client workspace controller
- Keep the authenticated route server-rendered for bootstrap and auth safety.
- Hydrate into a client workspace controller that owns panel selection, optimistic review state, and session advance actions.
- Avoid making the entire route client-only; the current server-side data access is valuable and already works.

### 2. Artifact registry by kind
- Introduce artifact renderers keyed by `kind`:
  - `question`
  - `jd-analysis`
  - `research-summary`
  - `interrogation-question`
  - `session-context`
  - `blueprint`
  - `draft-package`
  - `evaluation-scorecard`
- Use a generic fallback renderer for unknown artifacts so backend evolution does not immediately break the workspace.

### 3. Chat-centered workspace layout
- Primary column:
  - active session narrative
  - current prompt/review surface
  - stage-aware call to action
- Secondary column:
  - contextual artifact panel
  - vault snapshot or trace summary depending on stage
- Preserve the current broad split layout on desktop, but let the panel collapse into tabs or drawers on narrower widths.

### 4. Stage-aware default paneling
- Default the side panel based on the active stage:
  - `jd_analysis_review` -> JD analysis + research
  - `career_intake` -> interrogation question + relevant vault memory
  - `blueprint_review` -> blueprint + omitted signals
  - `draft_review` -> draft package + scorecard + actions
- Let the user override the panel, but do not force them to hunt for the active artifact.

### 5. Review interactions
- Inline actions should exist where the artifact is being read:
  - approve
  - reject
  - request revision
  - accept draft review
- Phase 4 should introduce visible diffs for artifacts that can change across revisions, especially blueprint and draft package content.

### 6. Motion and accessibility
- Use motion only for orientation: panel swaps, diff reveals, and review-state transitions.
- Keep action controls keyboard reachable and label state transitions clearly.
- Avoid hiding critical state behind hover-only UI.

## Implementation Recommendation

Start with a typed workspace shell and artifact registry before adding bespoke interactions. That keeps Phase 4 grounded in the Phase 3 contracts and reduces the chance of building a visually nice UI around unstable data assumptions.

## Risks

- If the first pass hardcodes rendering too tightly to the current artifact set, Phase 5 changes will be expensive.
- If the UI chases polish before interaction model clarity, approvals and reruns will still feel confusing.
- If all session mutations stay server-only without a client bridge, the review UX will remain sluggish or awkward.

## Suggested UI Sequence

1. Build the chat-centered shell and contextual panel switcher.
2. Add kind-aware artifact cards and stage-aware default views.
3. Add review actions and diff rendering.
4. Add trace summary/detail toggles and final accessibility polish.

---

*Phase: 04-frontend-experience*
*Research captured: 2026-04-05*
