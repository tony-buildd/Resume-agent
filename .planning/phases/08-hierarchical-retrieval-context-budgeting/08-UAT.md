# Phase 8 UAT

## Scope

Validate that large vaults and growing session context can still feed blueprinting through explicit evidence selection and budget traces.

## Checks

1. Retrieval narrows from roles to stories to evidence and exposes selection traces.
2. Context assembly respects stage token budgets and summarizes older entries only when needed.
3. Blueprint review consumes configurable evidence budgets and persists retrieval/budget artifacts.
4. Session envelopes expose `contextBudgetSummary` for the active run.

## Result

Pass.

## Evidence

- backend retrieval smoke for role/story/evidence selection and `selectionTraces`
- `pnpm typecheck:web`
- backend context-budget helper smoke for compression behavior
- API smoke for `contextBudgetSummary`
- API smoke for blueprint `budgetPolicy` and `selectionTraces`
