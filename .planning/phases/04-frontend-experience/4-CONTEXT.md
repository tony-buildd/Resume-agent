# Phase 4: Frontend Experience - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn the current API-backed workspace shell into an inspectable, chat-centered product UI. This phase covers the visible conversation area, contextual artifact panels, inline approval/edit/reject controls, diff review, and trace summaries. It does not add new backend orchestration stages unless the UI surface requires small supporting contract changes.

</domain>

<decisions>
## Implementation Decisions

### Workspace structure
- **D-01:** The conversation column should become the primary surface; stage state and artifacts should support it rather than dominate the page.
- **D-02:** Artifact panels should be contextual and selectable, not dumped as one long stack of raw cards.
- **D-03:** The UI must preserve inspectability: artifact kind, approval state, and trace rationale stay visible.

### Interaction model
- **D-04:** Approval flows should happen inline near the active artifact instead of requiring users to scan a generic artifact list.
- **D-05:** Diff review should exist for edited artifacts so changes feel strategic rather than magical.
- **D-06:** Trace history needs a compact summary mode plus an expandable debug/detail mode.

### Frontend architecture
- **D-07:** Keep the App Router workspace route server-rendered at the entry boundary, but move interactive review state into client components.
- **D-08:** Session and artifact rendering should use typed view-model helpers keyed by artifact kind so new runtime artifacts do not force a full page rewrite.
- **D-09:** The UI should accommodate both `resume` and `vault` modes without splitting into unrelated designs.

### Design direction
- **D-10:** Preserve the existing light-mode product language only as a starting point; Phase 4 should feel more editorial and intentional than a default admin dashboard.
- **D-11:** Panel transitions, approval states, and diff reveals should use restrained purposeful motion.
- **D-12:** Accessibility is a release criterion for this phase, especially for focus order, keyboard actions, and state announcements.

### the agent's Discretion
- Exact panel layout and breakpoint behavior
- Whether artifact tabs, pills, or a segmented control best represent the contextual side panel
- Whether diff rendering uses line-level or block-level comparisons in the first pass
- Which artifact kinds deserve bespoke cards immediately versus a generic fallback renderer

</decisions>

<specifics>
## Specific Ideas

- The workspace should feel like “strategy desk + evidence board,” not “session inspector.”
- The active stage should drive the default panel selection automatically, while still letting users inspect older artifacts.
- The right panel should help the user act on the current step: approve, reject, review, compare, or understand why the system asked something.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product and requirement scope
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

### Prior phase outputs the UI must render
- `.planning/phases/03-resume-session-flow/03-UAT.md`
- `.planning/phases/03-resume-session-flow/03-03-SUMMARY.md`
- `.planning/phases/03-resume-session-flow/03-04-SUMMARY.md`

### Existing frontend foundation
- `apps/web/src/app/(workspace)/workspace/page.tsx`
- `apps/web/src/app/globals.css`
- `apps/web/src/lib/api/sessions.ts`
- `apps/web/src/lib/api/vault.ts`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `apps/web/src/app/(workspace)/workspace/page.tsx` already renders authenticated session state, artifacts, trace events, and vault role summaries from the API.
- `apps/web/src/lib/api/sessions.ts` and `apps/web/src/lib/api/vault.ts` already provide typed server-side data access for the workspace route.
- `apps/web/src/app/globals.css` currently defines only a minimal neutral theme, leaving room for a more deliberate Phase 4 visual system.

### Current Gaps
- The workspace is still a static two-column diagnostic page, not a chat-first experience.
- Artifacts are rendered generically instead of by kind, so JD analysis, blueprint, draft package, and scorecard all look equally raw.
- There are no inline actions for approval or revision requests, and no diff visualization for edited content.
- Trace history is readable but unprioritized; it lacks a compact summary layer.

### Integration Points
- Phase 4 should render the existing session artifact kinds directly instead of inventing a parallel frontend-only state shape.
- The new `draft-package` and `evaluation-scorecard` artifacts from Phase 3 are the main Phase 4 rendering targets.
- Client components will likely need a client-safe session-advance bridge while the server route continues to own auth/bootstrap.

</code_context>

<deferred>
## Deferred Ideas

- Multi-session workspace switching and advanced search
- Polished mobile-specific layouts beyond responsive collapse behavior
- Export-quality print preview and resume theming controls

</deferred>

---

*Phase: 04-frontend-experience*
*Context gathered: 2026-04-05*
