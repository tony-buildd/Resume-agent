#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.orchestration.contracts import PaperDesignInputRecord  # noqa: E402
from app.orchestration.paper_design import build_paper_design_brief  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Turn a paper summary fixture into a Paper2Code-style design brief."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a JSON file with paperTitle, abstract, keyFindings, and implementationGoal.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the generated design brief JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    payload = json.loads(input_path.read_text())
    brief = build_paper_design_brief(PaperDesignInputRecord.model_validate(payload))
    output = json.dumps(brief.model_dump(by_alias=True, mode="json"), indent=2)
    if args.output:
        Path(args.output).expanduser().resolve().write_text(output + "\n")
    else:
        print(output)


if __name__ == "__main__":
    main()
