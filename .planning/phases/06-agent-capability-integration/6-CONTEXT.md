# Phase 6 Context

## User Goal

Set up external capability sources so they work for Codex in this project:

1. `huggingface/skills`
2. `affaan-m/everything-claude-code`
3. local `hermes-agent`
4. `going-doer/paper2code`
5. a Codex-usable Browser Use skill based on the provided AGENTS.md guidance

## Constraints

- Keep the project GSD-native even though the prior roadmap is complete.
- Commit and push every small step.
- Do not expose secrets from local environment files.
- Prefer Codex-native skills and wrappers over copying unrelated harness config into the repo.

## Source Findings

- `huggingface/skills` is already Codex-compatible and documents direct `.agents/skills` installation.
- `everything-claude-code` contains useful `.agents/skills`, but much of the repo is Claude/Cursor/OpenCode-specific and should not be mirrored wholesale.
- `paper2code` is a workflow repo, not a Codex skill pack, so it needs a local wrapper skill/helper path.
- `hermes-agent` is installed locally under `~/.hermes/hermes-agent`, but no Codex-facing wrapper exists in this repo yet.
- Browser Use guidance was provided directly by the user and should become a local Codex skill with project-specific defaults.
