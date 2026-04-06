---
status: complete
phase: 02-career-vault
source: 02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md
started: 2026-04-05T22:10:00-07:00
updated: 2026-04-06T00:56:00-07:00
---

## Current Test

[testing complete]

## Tests

### 1. Canonical vault create/list round-trip

expected: A user-scoped nested role tree with company, stories, facts, and candidate bullets can be created and listed without duplicating child records.
result: pass

### 2. Guided vault interview session lifecycle

expected: A vault interview session can move from seed prompt to focused role capture to checkpoint approval and persist the reviewed role into canonical vault storage.
result: pass

### 3. Workspace vault visibility

expected: The protected workspace can bootstrap a vault-mode session, surface the active vault prompt or checkpoint state, and list canonical vault roles.
result: pass

### 4. Review-state-aware retrieval boundaries

expected: Retrieval returns approved/user-stated draft-safe material for drafting, includes inferred material only in questioning-safe outputs, and excludes rejected material from both.
result: pass

### 5. Chroma sidecar semantic recall

expected: Long-form vault notes can be indexed in Chroma through an isolated adapter and queried semantically without replacing Postgres as the canonical store.
result: pass

### 6. API-level vault retrieval contract

expected: The FastAPI retrieval endpoint returns typed `draftSafeRoles`, `questioningSafeRoles`, and semantic matches for an authenticated user.
result: pass

## Summary

total: 6
passed: 6
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

[none yet]
