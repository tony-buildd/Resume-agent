# Phase 7 UAT

## Scope

Validate runtime hardening and memory safety without breaking the existing prototype flow.

## Checks

1. Session envelope exposes Phase 7 replan metadata and summary slots.
2. Explicit interruption intents reroute a session from the earliest affected stage.
3. Risky or unsupported evidence remains available for questioning but is excluded from draft-safe retrieval.
4. Runtime surfaces a memory-risk summary when questioning-only evidence exists.

## Result

Pass.

## Evidence

- backend contract smoke for new memory-safety fields
- API smoke for `clarify_fact` interruption reroute
- API smoke for `requestRevision` replan metadata
- retrieval smoke for questioning-safe vs draft-safe evidence filtering
- API smoke for `memoryRiskSummary`
