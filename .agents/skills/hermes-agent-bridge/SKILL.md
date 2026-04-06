---
name: hermes-agent-bridge
description: Use the locally installed Hermes Agent intentionally from Codex for sidecar agent work, diagnostics, skill inspection, and comparative workflows.
---

# Hermes Agent Bridge

Use this skill when the user wants to leverage the local Hermes installation from Codex rather than replacing Codex with Hermes.

## Local Assumptions

- Hermes CLI is expected at `hermes` on `PATH`.
- In this environment it is installed under `~/.local/bin/hermes`.
- The Hermes home is typically `~/.hermes/`.

## What Hermes Is Good For

- Inspecting Hermes-managed skills and plugins
- Running Hermes sidecar chats or sessions for comparison
- Checking Hermes configuration and health
- Exploring Hermes MCP, cron, memory, and plugin surfaces

## Safe First Commands

```bash
hermes --help
hermes doctor
hermes status
hermes skills --help
hermes plugins --help
hermes mcp --help
```

## Usage Rules

- Prefer the `hermes` entrypoint over `hermes-agent`.
- Treat Hermes as a sidecar toolchain, not the primary harness for this repo.
- Do not mutate Hermes config or credentials unless the user explicitly asks.
- When comparing Hermes and Codex capabilities, keep the comparison factual: skills, plugins, memory, MCP, cron, and multi-platform messaging are Hermes strengths.

## When To Use

- User asks whether Hermes can help with a workflow
- You need to inspect the Hermes skill or plugin catalog
- You want a second agent environment for sidecar experimentation
- You need to verify Hermes is installed and healthy

## When Not To Use

- Do not route ordinary repo coding tasks through Hermes by default.
- Do not assume Hermes has the same tool or permission model as Codex.
