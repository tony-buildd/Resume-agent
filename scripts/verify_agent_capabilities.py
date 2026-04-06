#!/usr/bin/env python3
"""Verify local external agent capability setup for this repo."""

from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

SKILLS = [
    "hf-cli",
    "huggingface-papers",
    "huggingface-jobs",
    "transformers-js",
    "ecc-verification-loop",
    "ecc-deep-research",
    "ecc-api-design",
    "browser-use-agent",
    "hermes-agent-bridge",
    "paper2code-workflow",
]


def exists(path: Path) -> bool:
    return path.exists()


def check_skill_paths() -> list[str]:
    results = []
    for skill in SKILLS:
        skill_md = REPO_ROOT / ".agents" / "skills" / skill / "SKILL.md"
        status = "PASS" if exists(skill_md) else "FAIL"
        results.append(f"{status} skill:{skill} -> {skill_md}")
    return results


def check_command(name: str) -> str:
    path = shutil.which(name)
    status = "PASS" if path else "WARN"
    return f"{status} command:{name} -> {path or 'not found'}"


def check_python_module(name: str) -> str:
    present = importlib.util.find_spec(name) is not None
    status = "PASS" if present else "WARN"
    return f"{status} module:{name} -> {'available' if present else 'not installed'}"


def main() -> None:
    checks = []
    checks.extend(check_skill_paths())
    checks.append(check_command("uv"))
    checks.append(check_command("hermes"))
    checks.append(check_python_module("browser_use"))
    checks.append(check_python_module("pydantic"))

    print("Agent capability verification")
    print("============================")
    for line in checks:
        print(line)


if __name__ == "__main__":
    main()
