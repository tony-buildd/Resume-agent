#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.orchestration.contracts import (  # noqa: E402
    JDAnalysisRecord,
    NarrativeBlueprintRecord,
    ResumePackageRecord,
)
from app.orchestration.evaluation import (  # noqa: E402
    build_trajectory_summary,
    evaluate_resume_package,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Replay a saved session fixture through the adaptive evaluator for offline QA."
        )
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a JSON fixture with analysis, blueprint, package, and optional runtime.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the replay result JSON.",
    )
    return parser.parse_args()


def load_fixture(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text())
    if not isinstance(payload, dict):
        raise ValueError("Replay fixture must be a JSON object.")
    return payload


def build_replay_payload(fixture: dict[str, Any]) -> dict[str, Any]:
    analysis = JDAnalysisRecord.model_validate(fixture["analysis"])
    blueprint = NarrativeBlueprintRecord.model_validate(fixture["blueprint"])
    package = ResumePackageRecord.model_validate(fixture["package"])
    runtime = fixture.get("runtime") or {}

    scorecard = evaluate_resume_package(
        blueprint=blueprint,
        package=package,
        analysis=analysis,
        runtime=runtime,
    )
    trajectory_summary = build_trajectory_summary(scorecard)

    return {
        "fixtureName": fixture.get("fixtureName"),
        "scorecard": scorecard.model_dump(by_alias=True, mode="json"),
        "trajectorySummary": trajectory_summary.model_dump(
            by_alias=True,
            mode="json",
        ),
    }


def main() -> None:
    args = parse_args()
    fixture_path = Path(args.input).expanduser().resolve()
    replay_payload = build_replay_payload(load_fixture(fixture_path))
    output = json.dumps(replay_payload, indent=2)

    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.write_text(output + "\n")
    else:
        print(output)


if __name__ == "__main__":
    main()
