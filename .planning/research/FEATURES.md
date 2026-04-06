# Feature Research

**Domain:** Agentic resume optimization platform
**Researched:** 2026-04-05
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

| Feature                              | Why Expected                                                  | Complexity | Notes                                     |
| ------------------------------------ | ------------------------------------------------------------- | ---------- | ----------------------------------------- |
| Role-specific JD analysis            | Resume tools must understand the target role before rewriting | MEDIUM     | This is the minimum bar for relevance     |
| Resume drafting and revision         | Users expect an editable draft, not only advice               | MEDIUM     | Markdown output is sufficient for MVP     |
| Persistent user memory               | The product thesis depends on retaining prior context         | HIGH       | Must support facts, provenance, and reuse |
| Authentication and private workspace | Career history and resume artifacts are personal data         | MEDIUM     | MVP can stay single-user scoped           |

### Differentiators (Competitive Advantage)

| Feature                                                 | Value Proposition                                              | Complexity | Notes                                 |
| ------------------------------------------------------- | -------------------------------------------------------------- | ---------- | ------------------------------------- |
| Visible multi-agent orchestration                       | Makes the product teachable, inspectable, and more trustworthy | HIGH       | Must avoid overwhelming the user      |
| Career vault with many candidate bullets per experience | Lets one role support multiple narratives for different jobs   | HIGH       | Central to long-term leverage         |
| Research-backed narrative strategy                      | Connects JD, company, and market context to resume angle       | HIGH       | Needs citations and concise summaries |
| Evaluator-guided targeted revisions                     | Makes the system act like a strategist, not just a writer      | MEDIUM     | Strong fit with the typed stage model |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature                                    | Why Requested                       | Why Problematic                                                               | Alternative                                  |
| ------------------------------------------ | ----------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------- |
| Full black-box autonomous rewriting        | Seems faster and more magical       | Destroys trust, hides unsupported claims, and undermines the learning goal    | Keep visible checkpoints and approval gates  |
| Huge upfront multi-section questionnaires  | Seems efficient for data collection | Feels like homework and slows first value                                     | Interview one role/story thread at a time    |
| Single canonical bullet set per experience | Simpler storage model               | Breaks the product thesis that one experience can support many job narratives | Store many candidate bullets linked to facts |

## Feature Dependencies

```text
Career Vault
    └──requires──> Foundations

Resume Session Flow
    └──requires──> Career Vault
    └──enhanced by──> Research

Frontend Workspace
    └──requires──> Foundations
    └──renders──> Vault + Session Flow artifacts
```

### Dependency Notes

- **Career Vault requires Foundations:** auth, storage, and orchestration contracts must exist first.
- **Resume Session Flow requires Career Vault:** the session has to retrieve durable user facts, not just fresh chat text.
- **Frontend Workspace depends on both:** the UI renders and controls artifacts produced by the backend stages.

## MVP Definition

### Launch With (v1)

- [ ] Authenticated chat-first workspace
- [ ] Career vault ingestion and fact/bullet storage
- [ ] JD + company/role research with citations
- [ ] Approved blueprint-driven resume generation
- [ ] Evaluator scorecard and targeted revisions

### Add After Validation (v1.x)

- [ ] Richer import sources and better parsing quality
- [ ] More export targets beyond markdown
- [ ] Saved application packet variants per employer

### Future Consideration (v2+)

- [ ] Collaboration / reviewer roles
- [ ] Enterprise auth and authorization
- [ ] Deeper portfolio and personal brand artifact generation

## Feature Prioritization Matrix

| Feature                            | User Value | Implementation Cost | Priority |
| ---------------------------------- | ---------- | ------------------- | -------- |
| Career vault + provenance          | HIGH       | HIGH                | P1       |
| JD analysis + research             | HIGH       | MEDIUM              | P1       |
| Blueprint + draft + evaluator loop | HIGH       | HIGH                | P1       |
| Inline artifact approvals          | HIGH       | MEDIUM              | P1       |
| Collaboration and sharing          | MEDIUM     | HIGH                | P3       |

## Competitor Feature Analysis

| Feature        | Competitor A          | Competitor B       | Our Approach                                      |
| -------------- | --------------------- | ------------------ | ------------------------------------------------- |
| Resume rewrite | Generic single prompt | Template-led draft | Typed, multi-stage, approval-gated drafting       |
| Memory         | Usually ephemeral     | Limited saved docs | Structured career vault with facts + many bullets |
| Transparency   | Mostly black box      | Partial hints      | Trace summaries, citations, diffs, scorecards     |

## Sources

- Bootstrap synthesis from approved product direction
- User problem framing captured in `.planning/PROJECT.md`
- Detailed market validation should happen during Phase 3 planning

---

_Feature research for: agentic resume optimization platform_
_Researched: 2026-04-05_
