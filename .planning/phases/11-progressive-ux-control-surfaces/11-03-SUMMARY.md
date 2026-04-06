# Summary 11-03

## Outcome

Added evaluator and routing drilldowns through selectable artifact surfaces:

- draft review now defaults to the evaluation scorecard for deeper rubric inspection
- JD analysis review prefers the richer strategy synthesis surface
- the artifact stream now acts as an explicit drilldown control via `artifactId`
- capability-route and strategy synthesis payloads render specialized drilldowns instead of falling back to generic JSON

## Verification

- `pnpm build:web`
- `pnpm typecheck:web`
