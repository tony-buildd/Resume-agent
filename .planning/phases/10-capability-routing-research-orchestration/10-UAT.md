# Phase 10 UAT

## Scope

Validate that research/tool routing is explicit, inspectable, and supported by the new architecture-research helper flow.

## Checks

1. JD intake persists a capability registry decision and route summary.
2. Research produces plan, source bundle, and strategy synthesis artifacts in addition to the existing review artifacts.
3. Capability routes expose explicit route traces.
4. Architecture-research notes can be turned into a Paper2Code-style design brief offline.

## Result

Pass.

## Evidence

- backend capability-route planner smoke
- runtime smoke for `capability-route`, `research-plan`, `source-bundle`, and `strategy-synthesis`
- runtime smoke for `routeTrace`
- `python3 scripts/paper_to_design_helper.py --input fixtures/papers/agent-routing-paper.json`
- `pnpm typecheck:web`
