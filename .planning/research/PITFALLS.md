# Pitfalls Research

**Domain:** Agentic resume optimization platform
**Researched:** 2026-04-05
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Treating the vault like a final resume

**What goes wrong:**
The product stores only a small set of polished bullets, so future tailoring sessions cannot recover alternate narratives or deeper evidence.

**Why it happens:**
Teams optimize for the first draft instead of durable memory design.

**How to avoid:**
Store hierarchical facts plus many candidate bullets per experience and make selection a session-time concern.

**Warning signs:**
One role has only three or four stored bullets with no fact provenance.

**Phase to address:**
Phase 2

---

### Pitfall 2: Opaque agent orchestration

**What goes wrong:**
The system feels magical at first, but users cannot tell why a question was asked or why a bullet changed.

**Why it happens:**
The product hides stage boundaries and prompt logic in the name of simplicity.

**How to avoid:**
Expose stage summaries, artifacts, approvals, and evaluator rationale while keeping deep details expandable.

**Warning signs:**
Users only see a final resume and cannot inspect the blueprint, research impact, or scorecard.

**Phase to address:**
Phases 1, 3, and 4

---

### Pitfall 3: Over-questioning the user

**What goes wrong:**
Sessions become long interviews with low signal, and users lose momentum before the first useful draft.

**Why it happens:**
The system optimizes for completeness instead of highest-value gaps.

**How to avoid:**
Ask one highest-impact question at a time and stop when marginal value drops.

**Warning signs:**
The session asks broad archival questions unrelated to the current JD.

**Phase to address:**
Phase 3

---

### Pitfall 4: Unsupported claims slipping into final output

**What goes wrong:**
The resume looks strong but contains invented or weakly supported claims the user cannot defend.

**Why it happens:**
Drafting draws from inference without visible provenance and approval gates.

**How to avoid:**
Separate `inferred` from `approved`, keep dormant facts questioning-only, and require approval before risky claims appear in drafts.

**Warning signs:**
The system cannot point from a bullet back to approved facts or user confirmation.

**Phase to address:**
Phases 2 and 3

---

### Pitfall 5: UI that collapses into generic chat

**What goes wrong:**
The user cannot inspect artifacts efficiently because everything is buried in a single chat stream.

**Why it happens:**
The frontend treats orchestration outputs as plain messages instead of first-class artifacts.

**How to avoid:**
Use a chat-centered workspace with contextual side panels, inline approvals, trace summaries, and diff views.

**Warning signs:**
Users have to scroll chat history to review blueprint decisions or resume revisions.

**Phase to address:**
Phase 4

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Store all memory as raw transcripts | Fast to prototype | Hard retrieval, no provenance, weak drafting safety | Only for throwaway prototypes |
| Skip artifact schemas | Less upfront code | Fragile orchestration and poor debuggability | Never for this product |
| Hide research citations | Cleaner UI at first glance | Lower trust and harder evaluation | Never if research influences strategy |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Clerk | Mixing auth identity with app authorization logic ad hoc | Keep clear user ownership boundaries in the app model |
| ChromaDB | Using embeddings as the canonical truth | Keep semantic retrieval secondary to relational facts |
| Search/browser tools | Letting external findings flow into drafts without review | Surface citations and strategic summaries first |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Overly chatty stage persistence | Slow session progression and bloated storage | Persist meaningful artifacts and events, not every token | Medium usage |
| Recomputing whole sessions on every change | Slow revisions and wasted tokens | Rerun from the earliest affected stage | Low to medium usage |
| Large unstructured vault retrieval | Irrelevant context injection and draft drift | Keep normalized entities and scoped retrieval | Medium usage |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Weak per-user scoping on vault/session records | Data leakage between users | Enforce ownership checks at the API and query layer |
| Logging raw sensitive resume data without care | Privacy and compliance issues | Be explicit about what events and artifacts are stored |
| Blindly trusting imported source material | Corrupt or misleading facts enter the vault | Route imported content through review checkpoints |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Asking for too much too early | User fatigue before first value | Let tailoring begin after one strong role is captured |
| Stage transitions with no explanation | Feels random and robotic | Show brief "why this stage / why this question" context |
| Revision changes with no diff | User cannot trust what changed | Show inline diffs with rationale |

## "Looks Done But Isn't" Checklist

- [ ] **Vault ingestion:** Provenance is visible and not just stored internally.
- [ ] **Resume draft:** Every strong claim can be traced to approved facts.
- [ ] **Research stage:** Citations are visible and summaries explain strategic impact.
- [ ] **Workspace UI:** Artifact panels remain usable without forcing full chat scrollback.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Vault stored too little detail | HIGH | Backfill schema, re-ingest important stories, regenerate bullet candidates |
| Drafting used unsafe inference | MEDIUM | Tighten retrieval rules, add provenance guards, rerun affected drafts |
| UI hid orchestration state | MEDIUM | Introduce artifact panels and trace summaries without changing backend contracts |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Vault equals final resume | Phase 2 | Verify multiple bullets and stories survive for one role |
| Opaque orchestration | Phases 1 and 4 | Verify artifacts, traces, and approvals are inspectable |
| Over-questioning | Phase 3 | Verify questions are single, targeted, and stop when marginal value drops |
| Unsupported claims | Phases 2 and 3 | Verify final bullets reference approved facts only |

## Sources

- Bootstrap synthesis from user problem framing and product decisions
- GSD-native workflow goals captured during project initialization
- Deeper validation to continue during phase planning and implementation

---
*Pitfalls research for: agentic resume optimization platform*
*Researched: 2026-04-05*
