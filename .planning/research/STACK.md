# Stack Research

**Domain:** Agentic resume optimization platform
**Researched:** 2026-04-05
**Confidence:** MEDIUM

## Recommended Stack

### Core Technologies

| Technology | Version       | Purpose                                                              | Why Recommended                                                                                      |
| ---------- | ------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Next.js    | latest stable | User-facing web app and workspace shell                              | Strong fit for a chat-first product UI, server/client composition, and modern frontend patterns      |
| FastAPI    | latest stable | Backend API and orchestration host                                   | Productive Python service layer with clear typing, async support, and straightforward API ergonomics |
| LangGraph  | latest stable | Strict multi-stage orchestration runtime                             | Matches the product goal of building a visible, typed agent harness rather than loose prompt chains  |
| PostgreSQL | latest stable | System of record for users, sessions, artifacts, and vault structure | Durable relational source of truth for identity-linked app data                                      |
| ChromaDB   | latest stable | Semantic retrieval for long-form notes and prior answers             | Complements Postgres without replacing the relational memory model                                   |
| Clerk      | latest stable | Authentication and user session management                           | Fastest route to robust auth for an individual-user SaaS-style MVP                                   |

### Supporting Libraries

| Library                       | Version       | Purpose                                          | When to Use                                                |
| ----------------------------- | ------------- | ------------------------------------------------ | ---------------------------------------------------------- |
| React Query or TanStack Query | latest stable | Client-side data syncing for workspace artifacts | Use for session, vault, and artifact fetch/mutation flows  |
| Zod                           | latest stable | Shared runtime validation of typed payloads      | Use for stage input/output schemas and API payload safety  |
| Langfuse                      | latest stable | Prompt/version observability                     | Use once prompt versions and agent stage inspection matter |
| Playwright                    | latest stable | Browser-level E2E coverage                       | Use for critical session and workspace flows               |

### Development Tools

| Tool           | Purpose                                      | Notes                                                                        |
| -------------- | -------------------------------------------- | ---------------------------------------------------------------------------- |
| pnpm           | Frontend package management                  | Good fit for monorepo-friendly, fast installs                                |
| uv             | Python dependency and environment management | Keeps Python setup lighter than ad hoc virtualenv flows                      |
| Docker Compose | Local service orchestration                  | Helpful once Postgres and optional Chroma local services are needed together |

## Alternatives Considered

| Recommended         | Alternative           | When to Use Alternative                                                            |
| ------------------- | --------------------- | ---------------------------------------------------------------------------------- |
| Clerk               | WorkOS                | Prefer WorkOS when org/enterprise identity becomes first-class                     |
| Postgres + ChromaDB | Convex                | Prefer Convex only if a TS-first realtime backend becomes the product center       |
| LangGraph           | ad hoc prompt routing | Use ad hoc routing only for disposable prototypes, not for a typed harness product |

## What NOT to Use

| Avoid                                       | Why                                                                         | Use Instead                                         |
| ------------------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------- |
| Streamlit as the primary UI                 | Too limiting for a polished, inspectable multi-panel workspace              | Next.js                                             |
| Vector DB as the only source of truth       | Makes fact provenance, approval state, and artifact relationships too loose | Postgres + ChromaDB                                 |
| Opaque agent swarms without stage contracts | Hides failures and makes the system hard to debug or trust                  | LangGraph with explicit schemas and validator gates |

## Stack Patterns by Variant

**If MVP remains single-user / solo candidate focused:**

- Keep Clerk + Postgres + ChromaDB
- Keep auth/authorization simple and per-user scoped

**If the product expands toward team coaching or enterprise review:**

- Revisit auth/authorization and collaboration primitives
- Consider richer role models and shared artifact permissions

## Version Compatibility

| Package A                 | Compatible With                     | Notes                                                       |
| ------------------------- | ----------------------------------- | ----------------------------------------------------------- |
| Next.js (latest stable)   | React (bundled stable)              | Validate exact versions when Phase 1 scaffolding is planned |
| FastAPI (latest stable)   | Pydantic (bundled stable)           | Validate API typing conventions during Phase 1 planning     |
| LangGraph (latest stable) | Python runtime selected for backend | Validate exact Python version during Phase 1 planning       |

## Sources

- User-approved architecture and product decisions from bootstrap discussion
- GSD workflow constraints and project goals in `.planning/PROJECT.md`
- Validation of exact versions deferred to per-phase planning and implementation

---

_Stack research for: agentic resume optimization platform_
_Researched: 2026-04-05_
