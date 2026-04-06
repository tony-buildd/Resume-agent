# Phase 9 UAT

## Scope

Validate that evaluation now scores both draft quality and orchestration quality, and that the scorecard can be replayed offline for QA.

## Checks

1. Scorecards include rubric profile, weighted dimensions, and dimension evidence.
2. Draft review persists trajectory judgments and rerun recommendation guidance.
3. Session envelopes expose `trajectoryEvaluationSummary`.
4. Saved fixtures can be replayed offline through the evaluator without booting the full app runtime.

## Result

Pass.

## Evidence

- backend rubric smoke for systems-profile weighting
- runtime smoke for `trajectoryJudgments`, `rerunRecommendation`, and `trajectoryEvaluationSummary`
- `python3 scripts/replay_session_evaluation.py --input fixtures/evaluation/backend-platform-session.json`
- `pnpm typecheck:web`
