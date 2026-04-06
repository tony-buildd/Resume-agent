# Phase 11 UAT

## Scope

Validate that the workspace exposes the new runtime and research surfaces progressively without losing the chat-first flow.

## Checks

1. The workspace derives progressive surface modes and shows signal cards only when those summaries are available.
2. Interruption controls are available directly from the workspace for review-heavy stages.
3. Evaluation, routing, and research artifacts can be inspected through the artifact stream.
4. The web app still typechecks and builds cleanly after the final UI changes.

## Result

Pass.

## Evidence

- `pnpm build:web`
- `pnpm typecheck:web`
