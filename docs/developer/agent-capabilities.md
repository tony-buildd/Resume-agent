# Agent Capability Bootstrap

This repo now includes a Codex-native capability layer for selected external agent ecosystems and tools.

## What Is Installed In The Repo

Repo-local skills live in [.agents/skills](/Users/minhthiennguyen/Desktop/agentic-resume-optimizer/.agents/skills).

Integrated upstream skills:

- `hf-cli`
- `huggingface-papers`
- `huggingface-jobs`
- `transformers-js`
- `ecc-verification-loop`
- `ecc-deep-research`
- `ecc-api-design`

Local bridge skills:

- `browser-use-agent`
- `hermes-agent-bridge`
- `paper2code-workflow`

## Bootstrap The Curated Upstream Skills

Refresh the upstream-backed repo-local skills with:

```bash
python3 scripts/bootstrap_agent_capabilities.py
```

This clones the selected upstream repos into `.cache/agent-capability-sources/` and copies curated skills into `.agents/skills/`.

## Verify The Capability Surface

Run:

```bash
python3 scripts/verify_agent_capabilities.py
```

This checks:

- expected repo-local skills
- `uv`
- `hermes`
- `browser-use`
- Python module availability signals

## Browser Use Notes

- Local install was validated with `uv tool install --python 3.12 browser-use`.
- `browser-use doctor` currently passes the core checks on Python `3.12`.
- Optional diagnostics may still mention `cloudflared` or `profile-use`; those are not blockers for normal local usage.
- If you want Browser Use Cloud, add `BROWSER_USE_API_KEY` to your local environment.

## Hermes Notes

- Hermes is available locally via `hermes`.
- Start with:

```bash
hermes --help
hermes doctor
hermes status
```

- Use the `hermes-agent-bridge` skill when you want Codex to intentionally interact with Hermes as a sidecar toolchain.

## Paper2Code Notes

- Paper2Code is treated as a workflow source, not a vendored dependency.
- Use the `paper2code-workflow` skill when you want Codex to turn papers into implementation plans or staged code generation.
- Upstream repo reference: [going-doer/paper2code](https://github.com/going-doer/paper2code)

## Why This Is Curated Instead Of Full Mirror

- `huggingface/skills` is Codex-native, so direct installation makes sense.
- `everything-claude-code` contains useful skills, but a full mirror would add many harness-specific or overlapping surfaces.
- Hermes and Paper2Code are tools/workflows, not drop-in Codex skill packs, so local bridge skills are the cleaner integration.
