# Phase 6 UAT

## Goal

Confirm that external capability sources are available to Codex through stable repo-local skills, scripts, and local tool checks.

## Checks

1. `python3 scripts/bootstrap_agent_capabilities.py`
   - Result: PASS
   - Curated Hugging Face and ECC skills refreshed into `.agents/skills`

2. `python3 scripts/verify_agent_capabilities.py`
   - Result: PASS with informational note
   - Repo-local skills present; `uv`, `hermes`, and `browser-use` commands detected
   - `browser_use` Python module is not installed in the system interpreter, which is acceptable because Browser Use is installed as a `uv` tool

3. `browser-use doctor`
   - Result: PASS with optional diagnostics
   - Core checks passed after reinstalling Browser Use with Python `3.12`
   - Optional `cloudflared` / `profile-use` items remain uninstalled

4. `hermes --help`
   - Result: PASS
   - Hermes CLI available for local sidecar use

## Conclusion

Phase 6 goals are satisfied for the first prototype. Codex now has a repo-local capability surface for curated external skills plus local bridge skills for Browser Use, Hermes, and Paper2Code.
