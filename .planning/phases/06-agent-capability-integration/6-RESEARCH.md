# Phase 6 Research

## Integration Strategy

### Hugging Face Skills

- Best fit for direct Codex consumption.
- Installation model: copy or symlink chosen skill folders into repo-local `.agents/skills`.
- Avoid duplicating names that are already globally available unless the repo needs pinned local copies.

### Everything-Claude-Code

- Treat as a capability source, not as a package to install wholesale.
- Prefer curated local wrappers or selected skills with non-conflicting names.
- Focus on repo-agnostic assets like verification, research, or coding standards rather than Claude-specific command surfaces.

### Hermes

- Hermes is a local CLI/tool environment, not a Codex skill repo.
- Best fit is a local bridging skill or operating doc that tells Codex when and how to use the installed CLI safely.

### Paper2Code

- Best fit is a local skill that codifies the planning -> analysis -> coding workflow and points to the external repo for execution details.
- Avoid vendoring the entire upstream project into this repo.

### Browser Use

- Best fit is a repo-local Codex skill because the user supplied explicit conventions and preferences.
- The skill should prefer `uv`, Pydantic v2 schemas, `pre-commit`, and `ChatBrowserUse`.
