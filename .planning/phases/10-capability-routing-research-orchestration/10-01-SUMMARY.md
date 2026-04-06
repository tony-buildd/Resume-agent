# Summary 10-01

## Outcome

Added a typed capability registry and persisted route metadata into JD intake:

- research capabilities now carry scope, latency, trust, auth, and structured-output metadata
- JD intake persists a `capability-route` artifact and `capabilityRouteSummary`
- route planning now explicitly records selected, deferred, and fallback capabilities

## Verification

- backend capability-route planner smoke
- runtime smoke for `capability-route` artifact and envelope summary
- `pnpm typecheck:web`
