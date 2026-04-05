# Phase 3 Research: Resume Session Flow

**Phase:** 3 - Resume Session Flow
**Date:** 2026-04-06
**Confidence:** MEDIUM-HIGH

## Research Focus

Phase 3 needs to turn the completed Career Vault into a controllable JD-to-resume pipeline. The key design risk is letting research, questioning, and drafting collapse into one prompt chain, which would erase the trust boundaries established in Phase 2.

## Recommended Phase Approach

### Orchestration shape
- Keep the Phase 1 runtime shell and expand it with Phase 3 stages rather than introducing a second orchestration engine.
- Represent JD analysis, research, blueprint, draft, and evaluator outputs as first-class artifacts with trace events.
- Reuse the interrupt pattern already proven in Phase 1 and Phase 2 for:
  - missing JD input
  - missing experience details
  - JD analysis approval
  - blueprint approval

### Research layering
- Split the early flow into:
  1. `JD analysis` - structured requirement extraction from the user-provided JD
  2. `company research` - browser-backed cited enrichment when useful
  3. `strategy summary` - concise explanation of how the research should alter the resume
- Store cited research separately from the distilled strategy so the UI can show both “raw evidence” and “what this means.”

### Vault usage
- Use `questioningSafeRoles` and semantic note matches during gap analysis and follow-up question generation.
- Use only `draftSafeRoles` when generating the narrative blueprint and draft package.
- Preserve many candidate bullets per role and let later stages pick the subset that survives the one-page budget.

### Writing and evaluation
- Make `Strategist` output a blueprint only, not prose.
- Make `Writer` output:
  - one-page markdown resume
  - talking points / concern-handling notes
- Make `Evaluator` score:
  - fit to JD
  - evidence support
  - specificity
  - overstatement risk
- Use evaluator results to reroute to the earliest affected stage, not to force a full redraft every time.

## OpenAI Research Notes

### Current API surface
- OpenAI’s current docs position the `Responses API` as the modern surface for tool-using, stateful interactions, with structured JSON text outputs and tool selection controls in the same API family.
- The Responses API reference also shows built-in tools, MCP tools, and custom function calls under one request shape, which matches this project’s agent-harness goal better than a plain chat-only flow.

### Model guidance
- OpenAI’s current models docs recommend `GPT-5.2` or `GPT-5.1` for most API usage.
- The current GPT-5.x model pages explicitly list `structured outputs` support and `Responses` endpoint support, which matters because this phase depends on typed artifacts and tool usage.

### Planning implication
- For Phase 3, prefer a small OpenAI adapter built around the Responses API and typed JSON outputs.
- Keep the adapter thin enough that a later Anthropic implementation can replace the provider call layer without rewriting session/runtime logic.

## Skill Audit

### GSD Skills

| Skill | Decision | Why |
|-------|----------|-----|
| `gsd-discuss-phase` | Used | Phase 3 needed fresh product/runtime decisions before planning |
| `gsd-plan-phase` | Deferred | Use after the Phase 3 context and research docs are written |
| `gsd-execute-phase` | Deferred | Use after the plan files are ready |
| `gsd-verify-work` | Deferred | Use after Phase 3 implementation exists |
| `gsd-add-tests` | Deferred | Add after completed session-flow behavior exists |

### Non-GSD Skills

| Skill | Decision | Why |
|-------|----------|-----|
| `brainstorming` | Used | Needed to recheck the multi-stage flow design before planning |
| `openai-docs` | Used | Phase 3 depends on current OpenAI API guidance for structured outputs and tool-using flows |
| `frontend-design` | Deferred | Final workspace UX is a later phase concern |
| `vercel-react-best-practices` | Deferred | This phase is backend/runtime-heavy |

## Risks To Address In Planning

1. Do not let cited research and distilled strategy blur together into one artifact.
2. Do not let `questioningSafeRoles` leak into drafting or blueprint generation.
3. Keep user approvals explicit at the JD analysis and blueprint stages.
4. Avoid a monolithic “writer” stage that does research, strategy, drafting, and evaluation in one pass.

## Planning Implications

- Plan `03-01` should implement JD analysis and cited research artifacts on the existing session shell.
- Plan `03-02` should implement one-question-at-a-time interrogation plus approval gates and canonical edits.
- Plan `03-03` should implement narrative blueprinting, drafting, and the final package assembly.
- Plan `03-04` should implement evaluator scoring and earliest-stage reruns.

## Notes From Official Sources

- Responses API reference: [Responses API](https://platform.openai.com/docs/api-reference/responses/retrieve)
- Current models overview: [Models](https://platform.openai.com/docs/models)
- Current general model recommendation snapshot: [Using GPT-5.2](https://platform.openai.com/docs/guides/latest-model)
- GPT-5.2 model page showing structured outputs + Responses support: [GPT-5.2 Model](https://platform.openai.com/docs/models/gpt-5.2/)

---
*Phase research completed: 2026-04-06*
