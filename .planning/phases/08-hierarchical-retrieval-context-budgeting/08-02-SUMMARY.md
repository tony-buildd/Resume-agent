# Summary 08-02

## Outcome

Added stage-aware context budgeting to keep session inputs bounded without dropping high-signal user context:

- canonical session context is now assembled under per-stage token budgets
- older context entries compress into summaries only when the stage budget is exceeded
- session envelopes now expose a `contextBudgetSummary` artifact and summary slot for downstream inspection

## Verification

- pure helper smoke for budget compression and preservation of recent context
- API smoke for `contextBudgetSummary` emission after career intake
