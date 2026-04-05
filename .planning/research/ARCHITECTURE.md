# Architecture Research

**Domain:** Agentic resume optimization platform
**Researched:** 2026-04-05
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                      Next.js Workspace                       │
├─────────────────────────────────────────────────────────────┤
│  Chat Thread  Artifact Panels  Diff Review  Trace Summary  │
├─────────────────────────────────────────────────────────────┤
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│  Auth Gate  Session API  Vault API  Research API           │
│  Orchestration Runtime  Evaluator  Artifact Persistence    │
├─────────────────────────────────────────────────────────────┤
│                  Storage / External Services                 │
│  Postgres  ChromaDB  Clerk  Model Providers  Web Search    │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Workspace UI | Present chat, artifacts, approvals, diffs, and trace context | Next.js routes, React state, server/client components |
| Session Orchestrator | Advance typed stages until interrupt or completion | LangGraph with explicit stage schemas and validators |
| Career Vault | Store hierarchical user memory and bullet candidates | Postgres tables plus Chroma retrieval hooks |
| Research Layer | Gather JD/company/role evidence and summarize impact | Search adapters + citation-aware summarization |
| Evaluator | Score drafts and propose targeted revisions | Typed scoring service driven by stage artifacts |

## Recommended Project Structure

```text
apps/
├── web/                # Next.js workspace UI
└── api/                # FastAPI backend
packages/
├── schemas/            # Shared contracts and artifact types
├── prompts/            # Stage prompt templates and prompt metadata
└── ui/                 # Reusable UI primitives if needed
infra/
└── docker/             # Local service bootstrapping
```

### Structure Rationale

- **apps/web:** Keeps the user-facing workspace independent from orchestration runtime details.
- **apps/api:** Isolates Python orchestration and persistence concerns.
- **packages/schemas:** Prevents the frontend and backend from drifting on artifact contracts.

## Architectural Patterns

### Pattern 1: Typed stage contracts

**What:** Every top-level stage consumes and emits structured state.
**When to use:** Always for JD analysis, questioning, blueprinting, drafting, and evaluation.
**Trade-offs:** More upfront schema work, but much better debugging and replayability.

### Pattern 2: Human interrupt checkpoints

**What:** The graph auto-runs until a question, approval, or completion boundary.
**When to use:** For JD approval, blueprint approval, and user-answer collection.
**Trade-offs:** Slightly slower flow than fire-and-forget, but much higher trust.

### Pattern 3: Relational source of truth + semantic retrieval

**What:** Keep durable entities in Postgres and use Chroma only for fuzzy retrieval over long-form context.
**When to use:** Throughout vault and session design.
**Trade-offs:** Two storage systems to manage, but cleaner provenance and retrieval behavior.

## Data Flow

### Request Flow

```text
User Action
    ↓
Workspace UI → Session API → Orchestrator → Vault / Research / Evaluator
    ↓               ↓             ↓                 ↓
Artifact panel ← Persisted state ← Stage output ← Postgres / Chroma / Search
```

### Key Data Flows

1. **Vault ingestion:** imported material or user answer -> normalization -> fact/bullet storage -> review checkpoint.
2. **Resume session:** JD -> research + retrieval -> question loop -> blueprint -> draft -> evaluator -> targeted rerun.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-1k users | Single API service and single database are sufficient |
| 1k-100k users | Add caching, job queues, and more careful event/log retention |
| 100k+ users | Split heavy orchestration workloads and dedicated retrieval/search services |

### Scaling Priorities

1. **First bottleneck:** orchestration latency and artifact persistence size.
2. **Second bottleneck:** research cost/throughput and vault retrieval performance.

## Anti-Patterns

### Anti-Pattern 1: Vault equals final resume

**What people do:** Store only a trimmed bullet list per role.
**Why it's wrong:** It erases alternate narratives and weakens future tailoring.
**Do this instead:** Store many claim/evidence facts and many candidate bullets per experience.

### Anti-Pattern 2: Hidden prompt spaghetti

**What people do:** Put all logic into a giant untyped prompt chain.
**Why it's wrong:** Failures become untraceable and user trust drops.
**Do this instead:** Use explicit stage schemas, artifacts, and validator gates.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Clerk | session verification and user identity mapping | Keep app data user-scoped |
| Model providers | backend service adapters | Keep provider choice behind a service boundary |
| Web search/browser tools | research-only stage integrations | All research must retain citations |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| web ↔ api | HTTP/JSON with shared schemas | Artifact contracts should be explicit |
| orchestrator ↔ vault | service layer calls | Enforce retrieval safety by fact state |
| orchestrator ↔ evaluator | typed artifact handoff | Evaluator should score artifacts, not raw chat only |

## Sources

- Bootstrap synthesis from user-approved product architecture
- GSD-native workflow constraints captured during initialization
- Exact integration details should be validated in Phase 1 planning

---
*Architecture research for: agentic resume optimization platform*
*Researched: 2026-04-05*
