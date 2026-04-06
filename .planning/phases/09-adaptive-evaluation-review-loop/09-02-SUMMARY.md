# Summary 09-02

## Outcome

Added trajectory-aware evaluation and rerun guidance:

- scorecards now include `trajectoryJudgments` and `rerunRecommendation`
- draft review persists `trajectoryEvaluationSummary` into the session envelope
- revision requests now prefer the evaluator's rerun recommendation when choosing the earliest rerun stage

## Verification

- runtime smoke for trajectory judgments and rerun recommendation persistence
- `pnpm typecheck:web`
