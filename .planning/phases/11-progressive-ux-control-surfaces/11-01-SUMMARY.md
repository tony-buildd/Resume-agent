# Summary 11-01

## Outcome

Added progressive workspace states and compact runtime signal surfaces:

- the workspace now derives `micro`, `sidecar`, or `full inspection` modes from active session signals
- runtime signals for memory risk, context budget, capability routing, and trajectory evaluation are surfaced as dedicated cards
- vault checkpoint approvals now flow correctly through the session API route

## Verification

- `pnpm build:web`
- `pnpm typecheck:web`
