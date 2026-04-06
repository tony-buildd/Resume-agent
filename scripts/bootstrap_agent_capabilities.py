#!/usr/bin/env python3
"""Bootstrap curated external agent capabilities into repo-local Codex skills."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_ROOT = REPO_ROOT / ".cache" / "agent-capability-sources"
TARGET_ROOT = REPO_ROOT / ".agents" / "skills"
MANIFEST_PATH = REPO_ROOT / "scripts" / "agent_capabilities.json"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def repo_slug(repo_url: str) -> str:
    name = repo_url.rstrip("/").rsplit("/", 1)[-1]
    return name.removesuffix(".git")


def clone_or_update(repo_url: str, ref: str) -> Path:
    destination = CACHE_ROOT / repo_slug(repo_url)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists():
        run(["git", "fetch", "--depth", "1", "origin", ref], cwd=destination)
        run(["git", "checkout", "--force", "FETCH_HEAD"], cwd=destination)
    else:
        run(["git", "clone", "--depth", "1", "--branch", ref, repo_url, str(destination)])

    return destination


def rename_skill_frontmatter(skill_dir: Path, new_name: str) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return

    content = skill_file.read_text()
    if not content.startswith("---\n"):
        return

    updated = re.sub(r"(?m)^name:\s*.+$", f"name: {new_name}", content, count=1)
    skill_file.write_text(updated)


def install_skill(repo_checkout: Path, spec: dict[str, str]) -> Path:
    source_dir = repo_checkout / spec["source_path"]
    if not source_dir.exists():
        raise FileNotFoundError(f"Missing source path: {source_dir}")

    target_dir = TARGET_ROOT / spec["destination"]
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)

    rename_to = spec.get("rename_skill")
    if rename_to:
        rename_skill_frontmatter(target_dir, rename_to)

    return target_dir


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text())
    installed: list[str] = []

    for spec in manifest["sources"]:
        checkout = clone_or_update(spec["repo"], spec.get("ref", "main"))
        target = install_skill(checkout, spec)
        installed.append(str(target.relative_to(REPO_ROOT)))

    print("Installed skills:")
    for item in installed:
        print(f"- {item}")


if __name__ == "__main__":
    main()
