# Phase 2 Research: Career Vault

**Phase:** 2 - Career Vault
**Date:** 2026-04-05
**Confidence:** MEDIUM-HIGH

## Research Focus

Phase 2 needs a vault model that stays truthful, reusable across many target roles, and compatible with the Phase 1 session/artifact contracts. The main design risk is collapsing memory into either freeform vector blobs or resume-ready bullets too early.

## Recommended Phase Approach

### Canonical vault model

- Keep the canonical vault relational in `Postgres`.
- Model the core entities explicitly:
  - `VaultCompany`
  - `VaultRole`
  - `VaultProjectStory`
  - `VaultFact`
  - `VaultBulletCandidate`
  - optional source/ingestion record for imported materials and interview turns
- Keep facts and candidate bullets separate. Facts are reusable evidence; bullets are story-specific renderings that may share the same facts.

### Provenance and review state

- Use explicit review/provenance fields on facts and bullets rather than inferred conventions.
- Facts should at least encode:
  - source type (`seed_material`, `interview_answer`, `agent_inference`)
  - review state (`user_stated`, `inferred`, `approved`, `rejected`)
  - draft eligibility
- Candidate bullets should track whether they are safe for drafting or only useful for prompting/questioning.

### Ingestion architecture

- Split vault ingestion into two paths:
  - seed import path for resume/portfolio/profile material
  - guided interview path for one-role / one-project capture
- Keep ingestion structured enough that later phases can ask “what is still missing?” instead of reparsing the same freeform notes every session.
- Story checkpoint review should happen after a coherent role/project capture, not after every single extracted fact.

### Retrieval architecture

- Use `ChromaDB` only for long-form semantic retrieval over imported notes, interview answers, and explanation text.
- Keep retrieval layered:
  - relational query for canonical entities and review-state filtering
  - Chroma query for fuzzy recall of supporting notes
  - merge layer that enforces “questioning-safe” vs “draft-safe” outputs
- Preserve the ability to retrieve dormant/inferred material for follow-up questions without allowing that material into drafts by default.

## Skill Audit

### GSD Skills

| Skill               | Decision | Why                                                           |
| ------------------- | -------- | ------------------------------------------------------------- |
| `gsd-discuss-phase` | Used     | Phase context and locked vault decisions were needed first    |
| `gsd-plan-phase`    | Used     | Phase 2 needs explicit implementation slices before execution |
| `gsd-execute-phase` | Deferred | Use after the plan files are ready                            |
| `gsd-verify-work`   | Deferred | Use after Phase 2 implementation exists                       |
| `gsd-add-tests`     | Deferred | Add after completed vault behavior exists                     |

### Non-GSD Skills

| Skill             | Decision | Why                                                                    |
| ----------------- | -------- | ---------------------------------------------------------------------- |
| `brainstorming`   | Used     | Needed to clarify the vault trust model and data shape before planning |
| `openai-docs`     | Skipped  | Phase 2 does not depend on current OpenAI API behavior                 |
| `frontend-design` | Deferred | Vault UI polish is not the primary concern in this phase               |

## Risks To Address In Planning

1. Avoid mixing canonical facts and draft-ready bullets into one table or one status field.
2. Avoid making ChromaDB the authoritative store for career memory.
3. Preserve enough structure that later JD/session phases can ask targeted follow-up questions instead of re-ingesting text.
4. Make review-state filtering unavoidable in retrieval APIs so drafting cannot accidentally consume unapproved inferred facts.

## Planning Implications

- Plan `02-01` should establish the relational schema, typed contracts, and minimal CRUD/service layer for companies, roles, stories, facts, and bullets.
- Plan `02-02` should build seed import plus guided role/story ingestion and story checkpoint review behavior.
- Plan `02-03` should add retrieval/indexing rules with review-state filtering and Chroma-backed semantic recall for long-form notes.

## Notes From Primary Sources

- Chroma collections support storing documents, metadata, and ids separately, which fits long-form note indexing better than canonical entity storage.
- SQLAlchemy 2.0 relationship patterns and enum/json columns fit the vault’s hierarchical and stateful model without requiring a separate ORM strategy.
- LangGraph’s interrupt/persistence model reinforces the decision to keep vault ingestion attached to resumable session boundaries rather than building a disconnected import pipeline.

---

_Phase research completed: 2026-04-05_
