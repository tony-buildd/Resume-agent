# GSD Workflow

This repository is operated as a GSD-native project.

That means `.planning/` is not optional documentation. It is the project operating system.

## Core Files

- `.planning/PROJECT.md` — product thesis and locked high-level decisions
- `.planning/REQUIREMENTS.md` — requirements and traceability
- `.planning/ROADMAP.md` — milestone and phase structure
- `.planning/STATE.md` — current active position in the workflow

## Expected Lifecycle

For meaningful project work, the expected flow is:

1. discuss the phase
2. create or refine the phase plan
3. execute the phase in small steps
4. verify the work
5. write a summary
6. update roadmap and state

In this repo, that usually means:
- `gsd-discuss-phase`
- `gsd-plan-phase`
- `gsd-execute-phase`
- `gsd-verify-work`

## Required Update Discipline

When a meaningful slice is completed:

- commit the code or docs change
- write or update the relevant `*-SUMMARY.md`
- update `ROADMAP.md`
- update `STATE.md`
- push the branch

For completed phases:

- add a phase-level `UAT` file

## Small Commit Rule

This repo has been developed with very small commits and push-after-step discipline.

The intent is:
- easier review
- easier forensic recovery
- clearer project history
- less ambiguity about which change introduced which behavior

Do not batch many unrelated changes into one commit unless the work is inseparable.

## Working In Context

Before starting a new slice:

1. read `README.md`
2. read `.planning/STATE.md`
3. read the relevant phase context and plan files
4. inspect the latest phase summary/UAT when needed

This avoids reopening decisions that are already locked.

## What Not To Do

- do not treat `.planning/` as stale notes
- do not skip summary/state updates after major work
- do not bypass the roadmap for convenience
- do not silently rewrite operating assumptions without updating docs

## Practical Rule

If the code changed but `.planning/` still tells the old story, the repo is out of sync.
