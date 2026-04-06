# Summary 08-01

## Outcome

Replaced flat vault retrieval with hierarchical role -> story -> evidence selection:

- retrieval now ranks roles first, then project stories, then facts and bullet candidates
- request payloads support independent `storyLimit` and `evidenceLimit` controls
- retrieval responses now emit `selectionTraces` explaining why each role, story, and evidence item was kept

## Verification

- backend retrieval smoke for story-level narrowing and selection-trace emission
- `pnpm typecheck:web`
