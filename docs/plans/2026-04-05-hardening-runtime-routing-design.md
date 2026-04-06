# Hardening and Evolution Design

## Scope

This design captures the approved Phase 7-11 roadmap for the next Resume Agent milestone. The goal is to keep the current prototype working while hardening its weak internals in layers rather than restarting the product flow from scratch.

## Chosen Approach

### Approach A: Clean-slate runtime rewrite

Pros:

- Easier to design ideal contracts from scratch
- Less temporary backward compatibility code

Cons:

- High regression risk against a working prototype
- Breaks the GSD incremental workflow and small-commit cadence

### Approach B: Incremental hardening around existing contracts

Pros:

- Preserves current user flow and verification surface
- Lets each phase add one subsystem improvement without destabilizing the rest of the app
- Fits the user's explicit "different phases" requirement

Cons:

- Requires temporary compatibility layers while types evolve
- Some intermediate code will be more verbose

### Approach C: UX-first overhaul before backend hardening

Pros:

- Faster visible changes

Cons:

- Repeats the current weakness of masking backend limits with UI
- Would force the frontend to adapt twice as backend semantics change later

## Recommendation

Use Approach B. The product already works end to end. The right move is to harden memory, retrieval, evaluation, routing, and UX progressively while preserving the stage model and current session flow.

## Design Decisions

1. Treat trust and safety as separate concerns. Review state is not enough; memory tier, validation status, contamination risk, quarantine reason, and feasibility checks must be explicit.
2. Add interruption intents as first-class runtime events. Revisions should target the earliest affected stage instead of going through one generic revision path.
3. Replace flat retrieval with hierarchical retrieval plus context budgets before making the evaluator more complex.
4. Upgrade the evaluator after retrieval improves so the rubric scores better inputs and can judge trajectory quality.
5. Route research through a capability registry. Internal data and structured sources should be preferred over browser automation fallback.
6. Keep the workspace chat-first, but progressively reveal deeper control surfaces only when the task complexity justifies them.

## Phase Breakdown

- Phase 7 hardens runtime and memory safety
- Phase 8 scales retrieval and context budgeting
- Phase 9 replaces the evaluator with adaptive rubrics
- Phase 10 adds capability routing and research orchestration
- Phase 11 surfaces the new controls progressively in the UI

## Guardrails

- No clean-slate rewrite of top-level flow
- No hidden promotion of quarantined or low-confidence facts into drafting
- No browser-first research policy
- Paper2Code is a design aid only, not a code generator for this repository
