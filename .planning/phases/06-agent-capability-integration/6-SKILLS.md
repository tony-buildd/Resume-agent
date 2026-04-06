# Phase 6 Skill Audit

## GSD Skills Reviewed

- `gsd-new-milestone`: implied by the need to reopen planning after a completed roadmap
- `gsd-discuss-phase`: represented here through captured context and explicit phase decisions
- `gsd-plan-phase`: represented here through the phase plans below
- `gsd-execute-phase`: will be simulated through small commit-sized execution slices
- `gsd-verify-work`: required for capability smoke tests and setup validation

## Non-GSD Skills Reviewed

- `find-skills`: used to verify Codex installation conventions and external skill install strategy
- `brainstorming`: applicable because this is capability design work with multiple integration shapes
- `plugin-creator`: reviewed but deferred because this milestone needs skills/scripts first, not a new plugin package
- `skill-installer`: relevant for GitHub-hosted Codex-compatible skills
- `openai-docs`: not needed for this phase
- `vercel:agent-browser`: deferred; Browser Use setup is the direct target here

## Skill Decisions

- Use `skill-installer` conventions as the baseline for GitHub-backed Codex skill installs.
- Avoid forcing `plugin-creator` because the integrations are better modeled as repo-local skills plus bootstrap docs.
- Reuse external skill repos selectively instead of importing entire ecosystems with overlapping or conflicting names.
