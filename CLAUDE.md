<!-- GSD:project-start source:PROJECT.md -->

## Project

**Resume Agent**

Resume Agent is a chat-first, agentic resume optimization platform for individual candidates who want role-specific resumes that are sharper, more strategic, and better grounded than generic AI rewrites. It combines a visible multi-agent harness, external role and company research, and a persistent career vault so the system can tailor resumes against the job description without collapsing the user's story into bland summary text.

**Core Value:** Turn fragmented career context into a credible, strategically tailored one-page resume that matches a target role without hiding how the system reached its recommendations.

### Constraints

- **Tech stack**: Frontend should use `Next.js`; backend should use `Python`, `FastAPI`, and `LangGraph` — this is part of the learning goal.
- **Workflow**: Project work should be GSD-native — planning and execution must happen through `.planning/` artifacts and GSD phase flows.
- **Trust model**: Inferred claims cannot silently become final resume content — user approval is required.
- **UX**: The product must stay chat-first while still exposing artifacts, diffs, and traces.
<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

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

- Keep Clerk + Postgres + ChromaDB
- Keep auth/authorization simple and per-user scoped
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
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.

<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.

<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.

<!-- GSD:profile-end -->
