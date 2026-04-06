from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from app.orchestration.contracts import ContextBudgetSummaryRecord, StageKey

DEFAULT_STAGE_TOKEN_BUDGETS: dict[StageKey, int] = {
    StageKey.CAREER_INTAKE: 180,
    StageKey.BLUEPRINT_REVIEW: 240,
    StageKey.DRAFT_REVIEW: 320,
}
PRESERVE_LATEST_ITEMS = 2
COMPRESSED_WORD_LIMIT = 18


def apply_context_budget(
    canonical_context: Mapping[str, Any],
    *,
    stage: StageKey,
) -> tuple[dict[str, Any], ContextBudgetSummaryRecord]:
    token_budget = DEFAULT_STAGE_TOKEN_BUDGETS.get(stage, 240)
    working = deepcopy(dict(canonical_context))
    total_tokens = estimate_mapping_tokens(working)

    if total_tokens <= token_budget:
        return (
            working,
            ContextBudgetSummaryRecord(
                tokenBudget=token_budget,
                reservedBudget=token_budget,
                compressed=False,
                notes=["Canonical context fit within the current stage budget."],
            ),
        )

    items = list(working.items())
    preserved = dict(items[-PRESERVE_LATEST_ITEMS:])
    older_items = items[:-PRESERVE_LATEST_ITEMS]
    compressed_keys: list[str] = []

    for key, value in older_items:
        if not isinstance(value, dict):
            preserved[key] = value
            continue
        compressed_keys.append(key)
        preserved[key] = {
            **value,
            "answer": truncate_words(str(value.get("answer", ""))),
            "compressionMode": "summary",
        }

    compressed_total = estimate_mapping_tokens(preserved)

    return (
        preserved,
        ContextBudgetSummaryRecord(
            tokenBudget=token_budget,
            reservedBudget=max(token_budget - compressed_total, 0),
            compressed=True,
            notes=[
                "Older canonical context entries were summarized to fit the stage budget.",
                f"Compressed entries: {', '.join(compressed_keys) or 'none'}",
            ],
        ),
    )


def estimate_mapping_tokens(payload: Mapping[str, Any]) -> int:
    text = " ".join(flatten_values(payload))
    if not text:
        return 0
    return max(1, len(text.split()))


def flatten_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        flattened: list[str] = []
        for nested in value.values():
            flattened.extend(flatten_values(nested))
        return flattened
    if isinstance(value, list):
        flattened: list[str] = []
        for nested in value:
            flattened.extend(flatten_values(nested))
        return flattened
    return [str(value)]


def truncate_words(value: str) -> str:
    words = value.split()
    if len(words) <= COMPRESSED_WORD_LIMIT:
        return value
    return " ".join(words[:COMPRESSED_WORD_LIMIT]) + " ..."
