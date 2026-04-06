# Resume Agent

## What This Is

Resume Agent is a chat-first, agentic resume optimization platform for individual candidates who want role-specific resumes that are sharper, more strategic, and better grounded than generic AI rewrites. It combines a visible multi-agent harness, external role and company research, and a persistent career vault so the system can tailor resumes against the job description without collapsing the user's story into bland summary text.

## Core Value

Turn fragmented career context into a credible, strategically tailored one-page resume that matches a target role without hiding how the system reached its recommendations.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Bootstrap a GSD-native project workflow that keeps planning, execution, and verification artifacts in sync.
- [ ] Build a persistent career vault that stores structured facts, provenance, and many reusable bullet candidates per experience.
- [ ] Build a visible JD-to-resume orchestration flow with approvals, traces, scorecards, and targeted revision loops.

### Out of Scope

- Enterprise multi-tenant admin workflows — MVP is for individual candidates, not org-managed usage.
- Fully autonomous claim fabrication — the system may suggest aggressive framing, but the user must explicitly approve what appears in the final resume.
- Native mobile apps — web-first delivery keeps the product focused on the orchestration and memory system.

## Context

The product exists because generic chat tools often make resumes worse by simplifying away architecture depth, impact signals, and candidate personality. The user wants the system to act like a resume strategist and agentic harness, not a single-prompt copy editor. The repository should be run through GSD as the primary operating system, with explicit phase discussion, planning, execution, verification, and frequent commits.

The current product direction is:

- `Next.js` frontend with a chat-centered workspace and contextual side panels
- `FastAPI + LangGraph` backend with strict stage contracts
- `Clerk` authentication for individual users
- `Postgres + ChromaDB` memory architecture
- Visible traces, approvals, scorecards, and research summaries

## Constraints

- **Tech stack**: Frontend should use `Next.js`; backend should use `Python`, `FastAPI`, and `LangGraph` — this is part of the learning goal.
- **Workflow**: Project work should be GSD-native — planning and execution must happen through `.planning/` artifacts and GSD phase flows.
- **Trust model**: Inferred claims cannot silently become final resume content — user approval is required.
- **UX**: The product must stay chat-first while still exposing artifacts, diffs, and traces.

## Key Decisions

| Decision                                                  | Rationale                                                                                           | Outcome   |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------- | --------- |
| Use `FastAPI + LangGraph` for orchestration               | The product is explicitly about learning agent harness design in Python                             | — Pending |
| Use `Next.js` for the frontend                            | A modern web app fits the chat workspace and artifact panel UX better than Streamlit                | — Pending |
| Use `Clerk` for MVP auth                                  | The first user shape is individual candidates, not enterprise orgs                                  | — Pending |
| Use `Postgres + ChromaDB`                                 | App state needs a relational source of truth; semantic retrieval is secondary memory infrastructure | — Pending |
| Keep top-level agents behind strict typed stage contracts | The product should teach controllable agent systems, not opaque agent swarms                        | — Pending |
| Use GSD as the default project OS                         | The user wants phase-by-phase planning, execution, verification, and explicit skill usage           | — Pending |
| Perform a skill audit at the start of each phase          | The project should deliberately use relevant GSD and non-GSD skills without forcing irrelevant ones | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):

1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):

1. Full review of all sections
2. Core Value check -> still the right priority?
3. Audit Out of Scope -> reasons still valid?
4. Update Context with current state

---

_Last updated: 2026-04-05 after initialization_
