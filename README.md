# Resume Agent

Resume Agent is an agentic resume operating system, not a one-shot resume generator.

The goal is to help a candidate build a role-specific resume by forcing the system to do the hard work that normal AI tools usually skip:

- understand the job description deeply
- understand what the company is actually hiring for
- recover missing technical and impact details from the candidate's past work
- choose the right story from a large history of experiences
- generate a tailored resume only after the strategy is clear

## The Problem

Most AI resume tools make resumes worse, not better.

They usually take a job description and an existing resume, then rewrite the text in one pass. That creates a few common failures:

- they smooth the writing but lose the real technical depth
- they compress complex projects into generic bullets
- they have no durable memory of the candidate's actual work
- they optimize wording before they understand the hiring target
- they treat the resume like a grammar problem instead of a positioning problem

That is the core mistake.

A strong resume is not just "better writing." It is a strategic document. To produce one well, the system has to understand the market, the role, the company, the candidate's actual evidence, and the story that should be told from that evidence.

## What This Project Is

Resume Agent is designed as a strict multi-stage system with visible reasoning and human checkpoints.

Instead of asking the model to rewrite everything at once, the product breaks the work into explicit stages:

- JD analysis
- company and role research
- gap interrogation
- narrative blueprinting
- drafting
- evaluation
- targeted reruns

The system also keeps a long-term career vault so one experience can store many facts, stories, and candidate bullets. That matters because the same role may need to be framed very differently for different jobs.

## How It Is Different

### 1. It does not treat the existing resume as the source of truth

Most tools only know what is already on the resume.

Resume Agent assumes the resume is incomplete. It actively interrogates the user to recover missing architecture details, scale, metrics, ownership boundaries, and implementation specifics that were never written down properly.

### 2. It stores much more than the final resume

Most resume tools only keep the latest output.

Resume Agent stores:

- canonical career facts
- project stories
- provenance
- candidate bullets
- approved vs inferred evidence
- session artifacts and traces

That means the system can reuse strong material over time instead of starting from scratch every time a user applies to a new role.

### 3. It separates strategy from writing

Most AI JD-based resume tools jump straight from job description to rewritten bullets.

Resume Agent forces a strategist step before drafting. The system must decide:

- which roles survive the one-page budget
- which project threads matter
- which bullets should lead
- which signals are missing
- what the hiring manager needs to believe

Only then does it write.

### 4. It has visible trust boundaries

Most tools hide their reasoning and blur the line between user-stated facts and model-generated framing.

Resume Agent is built around inspectable artifacts and approvals. The user can see the JD analysis, blueprint, draft package, scorecard, and rerun path. The system can suggest stronger framing, but the architecture is designed to keep provenance visible.

### 5. It is built for role fit, not generic improvement

Many tools try to produce a "better resume" in the abstract.

Resume Agent treats the job description as the customer. The output is judged by whether it fits the role, the market, and the evidence the candidate can stand behind, not by whether the wording sounds polished in isolation.

## What Makes The Product Interesting

This project is also intentionally a learning vehicle for agentic systems.

The product is being built to explore:

- multi-stage agent orchestration
- human-in-the-loop approval boundaries
- long-term semantic + structured memory
- typed artifacts between agents
- reruns from the earliest affected stage instead of full restarts
- inspectable AI workflows rather than black-box prompting

So the value of the repo is not only the resume product itself, but also the agent harness behind it.

## Current Architecture

- Frontend: `Next.js`
- Backend: `FastAPI + LangGraph`
- Auth: `Clerk`
- Database: `Postgres`
- Memory sidecar: `ChromaDB`
- Workflow OS: GSD artifacts in `.planning/`

## Repo Structure

- `apps/web` — product UI
- `apps/api` — orchestration and persistence backend
- `.planning/` — roadmap, requirements, phase plans, summaries, and UAT artifacts
- `docs/` — developer onboarding, setup, architecture, and operations docs

## Current State

The core backend flow is already in place:

- JD analysis and research
- one-question interrogation
- narrative blueprinting
- draft package generation
- evaluator scorecards
- targeted reruns

The current work is focused on making that system legible in the frontend workspace.

## Developer Docs

- [Local setup](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/docs/developer/local-setup.md)
- [Environment variables](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/docs/developer/environment.md)
- [Developer onboarding](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/docs/developer/onboarding.md)
