# Phase 3: Resume Session Flow - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the core JD-to-resume orchestration flow on top of the completed Career Vault. This phase covers JD analysis, cited company/role research, one-question-at-a-time interrogation, approval gates, narrative blueprinting, draft generation, evaluator scoring, and targeted reruns. It does not deliver the final polished workspace UX for inline editing and diffs; that belongs primarily to Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Session architecture

- **D-01:** Phase 3 must extend the existing typed session/artifact/trace runtime instead of introducing a second orchestration path.
- **D-02:** Each major resume stage should persist its own artifact so the user can inspect the reasoning chain from JD analysis to final scorecard.
- **D-03:** User approvals must stay explicit at the `JD analysis` and `narrative blueprint` boundaries before drafting can proceed.

### Research and citations

- **D-04:** JD analysis should produce a structured artifact containing top requirements, archetype, repeated terms, seniority/domain signals, and success definition.
- **D-05:** Company and market research may use browser-backed search, but every externally-derived claim must carry source links or citations.
- **D-06:** Research should yield a short strategic summary explaining how the findings change resume direction, not just a blob of copied facts.

### Vault usage

- **D-07:** JD and research stages should read from the completed Career Vault retrieval surface instead of querying raw vault tables directly.
- **D-08:** Questioning stages may use `questioningSafeRoles` plus semantic note matches; drafting stages may use only `draftSafeRoles`.
- **D-09:** One targeted question at a time remains the interaction rule, and the question must explain why the missing signal matters.

### Writing flow

- **D-10:** The `Strategist` stage outputs a blueprint, not drafted prose.
- **D-11:** The `Writer` stage should generate the full one-page markdown resume plus interview notes package only after blueprint approval.
- **D-12:** The `Evaluator` stage scores fit, evidence support, specificity, and overstatement risk, then points reruns to the earliest affected stage instead of forcing a full restart.

### LLM/runtime choices

- **D-13:** Phase 3 should favor structured-output-capable OpenAI APIs for typed artifacts and tool-using orchestration.
- **D-14:** Responses API is the preferred OpenAI integration surface for this phase because the product needs stateful, tool-using, multi-stage interactions rather than plain chat completion.
- **D-15:** Provider details should stay behind a small adapter so later Anthropic support does not require rewiring the session runtime.

### the agent's Discretion

- Exact artifact naming and stage-key expansion inside the runtime
- Whether company research lives in a dedicated module or in the JD/research stage module
- Prompt template layout and typed output schemas per stage
- How much evaluator scoring is heuristic versus model-generated in the first pass

</decisions>

<specifics>
## Specific Ideas

- The JD is the customer, but the product still needs visible truth boundaries: aggressive framing can be suggested, but only approved facts can feed the draft.
- Phase 3 should prove the system can turn one strong vault role into a role-specific resume path even before the whole career history is complete.
- Resume sessions should feel like guided, inspectable strategy work instead of one giant prompt rewrite.

</specifics>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product and requirement scope

- `.planning/PROJECT.md` — Product framing, trust model, and locked stack decisions
- `.planning/REQUIREMENTS.md` — Research, session-flow, and writing requirements for Phase 3
- `.planning/ROADMAP.md` — Phase boundary and dependency on the completed Career Vault
- `.planning/STATE.md` — Current workflow state

### Prior phase foundation

- `.planning/phases/01-foundations/01-03-SUMMARY.md` — Typed session/runtime shell built in Phase 1
- `.planning/phases/02-career-vault/02-03-SUMMARY.md` — Vault retrieval and Chroma indexing surface
- `.planning/phases/02-career-vault/02-UAT.md` — Verified vault behaviors that Phase 3 can rely on
- `docs/architecture/foundation-contracts.md` — Current auth/session/artifact/trace contracts

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `apps/api/app/orchestration/contracts.py` - Current stage and artifact contract surface that Phase 3 will extend
- `apps/api/app/orchestration/runtime.py` - Deterministic runtime shell already supports interrupts, approvals, traces, and vault-mode routing
- `apps/api/app/api/routes/sessions.py` - Existing create/get/advance session endpoints for the main workspace flow
- `apps/api/app/vault/retrieval.py` - Typed draft-safe and questioning-safe vault recall for later research and drafting stages
- `apps/web/src/app/(workspace)/workspace/page.tsx` - Current workspace shell that already renders session state, artifacts, and traces

### Established Patterns

- Postgres remains the canonical store; Chroma is a semantic sidecar
- Artifacts and traces are explicit typed contracts rather than ad hoc JSON blobs
- Review-state boundaries are already enforced in vault retrieval

### Integration Points

- JD analysis and research should become first-class artifacts in the existing session envelope
- Interrogation should pull from the Career Vault retrieval surface rather than re-ask for already approved context
- Blueprint approval and evaluator reruns should reuse the same interrupt/approval pattern established in the current runtime

</code_context>

<deferred>
## Deferred Ideas

- Rich inline artifact editing and visual diff UX remain Phase 4 work
- Multiple resume variants per target company remain later milestone work
- Anthropic or multi-provider routing can wait until the OpenAI-backed Phase 3 flow is stable

</deferred>

---

_Phase: 03-resume-session-flow_
_Context gathered: 2026-04-06_
