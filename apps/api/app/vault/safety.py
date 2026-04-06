from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from app.db.models import (
    VaultBulletCandidate,
    VaultContaminationRisk,
    VaultFact,
    VaultMemoryTier,
    VaultProjectStory,
    VaultQuarantineReason,
    VaultReviewState,
    VaultRole,
    VaultValidationStatus,
)
from app.vault.contracts import VaultRoleRecord

METRIC_RE = re.compile(
    r"(?:(?:~|approx(?:imately)?|around)\s*)?\d[\d,]*(?:\.\d+)?(?:%|x|k|m|ms|s|sec|seconds|minutes|hrs|hours)?",
    re.IGNORECASE,
)
TOKEN_RE = re.compile(r"[a-z0-9]+")

RISK_ORDER = {
    VaultContaminationRisk.LOW: 0,
    VaultContaminationRisk.MEDIUM: 1,
    VaultContaminationRisk.HIGH: 2,
}
STATUS_ORDER = {
    VaultValidationStatus.UNCHECKED: 0,
    VaultValidationStatus.VALIDATED: 1,
    VaultValidationStatus.NEEDS_REVIEW: 2,
    VaultValidationStatus.FAILED: 3,
}


def hydrate_role_safety(role: VaultRole, *, company_name: str | None = None) -> None:
    prior_metric_signatures: dict[str, tuple[str, ...]] = {}

    role_facts = [fact for fact in role.facts if fact.project_story_id is None]
    for fact in role_facts:
        apply_fact_safety(
            fact,
            prior_metric_signatures=prior_metric_signatures,
            company_name=company_name,
        )

    for story in role.project_stories:
        for fact in story.facts:
            apply_fact_safety(
                fact,
                prior_metric_signatures=prior_metric_signatures,
                company_name=company_name,
            )
        for bullet in story.bullet_candidates:
            apply_bullet_safety(bullet)
        apply_story_safety(story)

    role_bullets = [
        bullet for bullet in role.bullet_candidates if bullet.project_story_id is None
    ]
    for bullet in role_bullets:
        apply_bullet_safety(bullet)


def summarize_memory_risks(roles: Iterable[VaultRoleRecord]) -> dict[str, object]:
    quarantined = 0
    high_risk = 0
    failed = 0

    for role in roles:
        for story in role.project_stories:
            quarantined += int(story.memory_tier is VaultMemoryTier.QUARANTINE)
            high_risk += int(story.contamination_risk is VaultContaminationRisk.HIGH)
            failed += int(story.validation_status is VaultValidationStatus.FAILED)
            for fact in story.facts:
                quarantined += int(fact.memory_tier is VaultMemoryTier.QUARANTINE)
                high_risk += int(fact.contamination_risk is VaultContaminationRisk.HIGH)
                failed += int(fact.validation_status is VaultValidationStatus.FAILED)
            for bullet in story.bullet_candidates:
                quarantined += int(bullet.memory_tier is VaultMemoryTier.QUARANTINE)
                high_risk += int(
                    bullet.contamination_risk is VaultContaminationRisk.HIGH
                )
                failed += int(bullet.validation_status is VaultValidationStatus.FAILED)

        for fact in role.role_facts:
            quarantined += int(fact.memory_tier is VaultMemoryTier.QUARANTINE)
            high_risk += int(fact.contamination_risk is VaultContaminationRisk.HIGH)
            failed += int(fact.validation_status is VaultValidationStatus.FAILED)
        for bullet in role.role_bullet_candidates:
            quarantined += int(bullet.memory_tier is VaultMemoryTier.QUARANTINE)
            high_risk += int(bullet.contamination_risk is VaultContaminationRisk.HIGH)
            failed += int(bullet.validation_status is VaultValidationStatus.FAILED)

    notes: list[str] = []
    if quarantined:
        notes.append("Quarantined evidence remains available for questioning only.")
    if failed:
        notes.append("Failed feasibility checks are blocked from drafting.")
    if high_risk:
        notes.append("High-risk evidence should be clarified before drafting.")

    return {
        "quarantinedItems": quarantined,
        "highRiskItems": high_risk,
        "failedFeasibilityItems": failed,
        "notes": notes,
    }


def is_draft_safe(item: Any) -> bool:
    return (
        item.review_state in {VaultReviewState.USER_STATED, VaultReviewState.APPROVED}
        and bool(item.draft_eligible)
        and item.memory_tier is VaultMemoryTier.CANONICAL
        and item.validation_status is VaultValidationStatus.VALIDATED
        and item.quarantine_reason is VaultQuarantineReason.NONE
        and item.contamination_risk is VaultContaminationRisk.LOW
    )


def is_questioning_safe(item: Any) -> bool:
    return item.review_state is not VaultReviewState.REJECTED


def apply_fact_safety(
    fact: VaultFact,
    *,
    prior_metric_signatures: dict[str, tuple[str, ...]],
    company_name: str | None = None,
) -> None:
    metrics = extract_metric_tokens(fact.statement)
    signature = semantic_signature(fact.statement)
    contradiction = (
        bool(metrics)
        and signature in prior_metric_signatures
        and prior_metric_signatures[signature] != metrics
    )
    if metrics and signature not in prior_metric_signatures:
        prior_metric_signatures[signature] = metrics

    unsupported_metric = bool(metrics) and fact.review_state is VaultReviewState.INFERRED and not fact.evidence
    cross_role = detect_cross_role_leakage(fact.statement, company_name)

    if contradiction:
        set_safety_fields(
            fact,
            memory_tier=VaultMemoryTier.QUARANTINE,
            validation_status=VaultValidationStatus.FAILED,
            contamination_risk=VaultContaminationRisk.HIGH,
            quarantine_reason=VaultQuarantineReason.CONTRADICTION,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=True,
                unsupported_metric=unsupported_metric,
                cross_role_leakage=cross_role,
            ),
        )
    elif unsupported_metric:
        set_safety_fields(
            fact,
            memory_tier=VaultMemoryTier.QUARANTINE,
            validation_status=VaultValidationStatus.FAILED,
            contamination_risk=VaultContaminationRisk.MEDIUM,
            quarantine_reason=VaultQuarantineReason.UNSUPPORTED_METRIC,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=False,
                unsupported_metric=True,
                cross_role_leakage=cross_role,
            ),
        )
    elif cross_role:
        set_safety_fields(
            fact,
            memory_tier=VaultMemoryTier.QUARANTINE,
            validation_status=VaultValidationStatus.FAILED,
            contamination_risk=VaultContaminationRisk.HIGH,
            quarantine_reason=VaultQuarantineReason.CROSS_ROLE_LEAKAGE,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=False,
                unsupported_metric=False,
                cross_role_leakage=True,
            ),
        )
    elif fact.review_state is VaultReviewState.INFERRED or (metrics and not fact.evidence):
        set_safety_fields(
            fact,
            memory_tier=VaultMemoryTier.FEASIBILITY,
            validation_status=VaultValidationStatus.NEEDS_REVIEW,
            contamination_risk=(
                VaultContaminationRisk.MEDIUM
                if fact.review_state is VaultReviewState.INFERRED
                else VaultContaminationRisk.LOW
            ),
            quarantine_reason=VaultQuarantineReason.NONE,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=False,
                unsupported_metric=False,
                cross_role_leakage=False,
            ),
        )
    else:
        set_safety_fields(
            fact,
            memory_tier=VaultMemoryTier.CANONICAL,
            validation_status=VaultValidationStatus.VALIDATED,
            contamination_risk=VaultContaminationRisk.LOW,
            quarantine_reason=VaultQuarantineReason.NONE,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=False,
                unsupported_metric=False,
                cross_role_leakage=False,
            ),
        )


def apply_bullet_safety(bullet: VaultBulletCandidate) -> None:
    metrics = extract_metric_tokens(bullet.text)
    supported_metrics = {
        metric
        for fact in bullet.supporting_facts
        for metric in extract_metric_tokens(fact.statement)
    }
    unsupported_metric = bool(metrics) and not set(metrics).issubset(supported_metrics)
    cross_role = any(resolve_role_id(fact) != resolve_role_id(bullet) for fact in bullet.supporting_facts)
    contradiction = any(
        fact.quarantine_reason is VaultQuarantineReason.CONTRADICTION
        for fact in bullet.supporting_facts
    )

    if cross_role:
        set_safety_fields(
            bullet,
            memory_tier=VaultMemoryTier.QUARANTINE,
            validation_status=VaultValidationStatus.FAILED,
            contamination_risk=VaultContaminationRisk.HIGH,
            quarantine_reason=VaultQuarantineReason.CROSS_ROLE_LEAKAGE,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=contradiction,
                unsupported_metric=unsupported_metric,
                cross_role_leakage=True,
            ),
        )
    elif contradiction:
        set_safety_fields(
            bullet,
            memory_tier=VaultMemoryTier.QUARANTINE,
            validation_status=VaultValidationStatus.FAILED,
            contamination_risk=VaultContaminationRisk.HIGH,
            quarantine_reason=VaultQuarantineReason.CONTRADICTION,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=True,
                unsupported_metric=unsupported_metric,
                cross_role_leakage=False,
            ),
        )
    elif unsupported_metric:
        set_safety_fields(
            bullet,
            memory_tier=VaultMemoryTier.QUARANTINE,
            validation_status=VaultValidationStatus.FAILED,
            contamination_risk=VaultContaminationRisk.MEDIUM,
            quarantine_reason=VaultQuarantineReason.UNSUPPORTED_METRIC,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=False,
                unsupported_metric=True,
                cross_role_leakage=False,
            ),
        )
    elif bullet.review_state is VaultReviewState.INFERRED or not bullet.supporting_facts:
        set_safety_fields(
            bullet,
            memory_tier=VaultMemoryTier.FEASIBILITY,
            validation_status=VaultValidationStatus.NEEDS_REVIEW,
            contamination_risk=VaultContaminationRisk.MEDIUM,
            quarantine_reason=VaultQuarantineReason.NONE,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=False,
                unsupported_metric=False,
                cross_role_leakage=False,
            ),
        )
    else:
        set_safety_fields(
            bullet,
            memory_tier=VaultMemoryTier.CANONICAL,
            validation_status=VaultValidationStatus.VALIDATED,
            contamination_risk=VaultContaminationRisk.LOW,
            quarantine_reason=VaultQuarantineReason.NONE,
            feasibility_checks=build_feasibility_checks(
                metrics=metrics,
                contradiction=False,
                unsupported_metric=False,
                cross_role_leakage=False,
            ),
        )


def apply_story_safety(story: VaultProjectStory) -> None:
    children = [*story.facts, *story.bullet_candidates]
    if any(item.memory_tier is VaultMemoryTier.QUARANTINE for item in children):
        memory_tier = VaultMemoryTier.QUARANTINE
    elif story.review_state is VaultReviewState.INFERRED or any(
        item.validation_status is not VaultValidationStatus.VALIDATED
        for item in children
    ):
        memory_tier = VaultMemoryTier.FEASIBILITY
    else:
        memory_tier = VaultMemoryTier.CANONICAL

    validation_status = max(
        (item.validation_status for item in children),
        key=lambda item: STATUS_ORDER[item],
        default=(
            VaultValidationStatus.NEEDS_REVIEW
            if story.review_state is VaultReviewState.INFERRED
            else VaultValidationStatus.VALIDATED
        ),
    )
    contamination_risk = max(
        (item.contamination_risk for item in children),
        key=lambda item: RISK_ORDER[item],
        default=VaultContaminationRisk.LOW,
    )
    quarantine_reason = next(
        (
            item.quarantine_reason
            for item in children
            if item.quarantine_reason is not VaultQuarantineReason.NONE
        ),
        VaultQuarantineReason.NONE,
    )
    set_safety_fields(
        story,
        memory_tier=memory_tier,
        validation_status=validation_status,
        contamination_risk=contamination_risk,
        quarantine_reason=quarantine_reason,
        feasibility_checks={
            "factCount": len(story.facts),
            "bulletCount": len(story.bullet_candidates),
            "quarantinedChildren": sum(
                1 for item in children if item.memory_tier is VaultMemoryTier.QUARANTINE
            ),
        },
    )


def set_safety_fields(
    item: Any,
    *,
    memory_tier: VaultMemoryTier,
    validation_status: VaultValidationStatus,
    contamination_risk: VaultContaminationRisk,
    quarantine_reason: VaultQuarantineReason,
    feasibility_checks: dict[str, object],
) -> None:
    item.memory_tier = memory_tier
    item.validation_status = validation_status
    item.contamination_risk = contamination_risk
    item.quarantine_reason = quarantine_reason
    item.feasibility_checks = feasibility_checks
    if validation_status is VaultValidationStatus.FAILED or memory_tier is VaultMemoryTier.QUARANTINE:
        item.draft_eligible = False


def extract_metric_tokens(text: str) -> tuple[str, ...]:
    return tuple(match.group(0).lower() for match in METRIC_RE.finditer(text))


def semantic_signature(text: str) -> str:
    stripped = METRIC_RE.sub(" ", text.lower())
    tokens = [token for token in TOKEN_RE.findall(stripped) if len(token) > 2]
    return " ".join(tokens[:8])


def detect_cross_role_leakage(text: str, company_name: str | None) -> bool:
    del text, company_name
    return False


def resolve_role_id(item: Any) -> str | None:
    if getattr(item, "role_id", None):
        return str(item.role_id)
    role = getattr(item, "role", None)
    return str(role.id) if role is not None and getattr(role, "id", None) else None


def build_feasibility_checks(
    *,
    metrics: tuple[str, ...],
    contradiction: bool,
    unsupported_metric: bool,
    cross_role_leakage: bool,
) -> dict[str, object]:
    return {
        "metricTokens": list(metrics),
        "contradiction": contradiction,
        "unsupportedMetric": unsupported_metric,
        "crossRoleLeakage": cross_role_leakage,
    }
