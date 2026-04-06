# Phase 7 Research

## Memory and Runtime Hardening

- Memory should be split into trust-oriented review state and safety-oriented validation/quarantine state.
- Runtime edits should be modeled as explicit intentful interruptions, not only generic "request revision" toggles.
- Evidence promotion should require feasibility checks so unsupported metrics or contradictory claims remain question-only material.

## Relevant Paper Findings

- Dual-memory and memory-safety work argues for separate progress, feasibility, and quarantine layers instead of one flat memory store.
- Interruption-focused agent papers argue that user changes should target the earliest affected stage rather than restarting the whole flow.
- Retrieval improvements are important, but Phase 7 should first ensure the system can safely decide what evidence is even allowed into later stages.
