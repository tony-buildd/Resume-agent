# Release Checklist

Use this checklist before calling a new state of the project “shippable”.

## Product Checks

- confirm the main resume session flow still works from JD intake to draft review
- confirm the workspace renders active artifacts correctly
- confirm review actions behave correctly for JD approval, blueprint approval, and draft revision
- confirm vault mode still renders and does not regress

## Quality Checks

- run `pnpm typecheck:web`
- run `pnpm lint:web`
- run `pnpm build:web`
- run `source .venv/bin/activate && pnpm check:api`

## Environment Checks

- verify required Clerk keys exist in the target environment
- verify `DATABASE_URL` is set correctly
- verify `RESUME_AGENT_API_URL` points to the deployed backend
- verify optional OpenAI config is either valid or intentionally absent

## Documentation Checks

- update `README.md` if the product position or architecture changed materially
- update `.env.example` if environment requirements changed
- update the relevant phase summary/UAT/state artifacts in `.planning/`
- update developer docs if setup or deployment steps changed

## GSD Checks

- confirm the relevant phase summary file exists
- confirm roadmap progress matches completed work
- confirm `.planning/STATE.md` points to the real next step
- confirm UAT exists for any completed phase

## Final Human Check

- ask: “Could another developer clone this repo and understand what is built, how to run it, and what comes next?”

If the answer is no, the release is not actually ready yet.
