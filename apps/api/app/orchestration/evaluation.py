from __future__ import annotations

import re

from app.orchestration.contracts import (
    EvaluationDimensionRecord,
    EvaluationScorecardRecord,
    JDAnalysisRecord,
    NarrativeBlueprintRecord,
    ResumePackageRecord,
    StageKey,
)


def evaluate_resume_package(
    *,
    blueprint: NarrativeBlueprintRecord,
    package: ResumePackageRecord,
    analysis: JDAnalysisRecord,
) -> EvaluationScorecardRecord:
    resume_text = package.markdown_resume.lower()
    covered_requirements = count_requirement_hits(analysis.top_requirements, resume_text)
    total_requirements = max(len(analysis.top_requirements), 1)
    omitted_count = len(blueprint.omitted_signals)
    bullets = [
        bullet
        for role in blueprint.selected_roles
        for bullet in role.selected_bullets
    ]
    quantified_bullets = sum(1 for bullet in bullets if has_metric(bullet.text))
    bullet_count = max(len(bullets), 1)

    fit_score = clamp_score(round(covered_requirements / total_requirements * 5))
    evidence_score = clamp_score(round((bullet_count - omitted_count) / bullet_count * 5))
    specificity_score = clamp_score(round(quantified_bullets / bullet_count * 5))
    overstatement_risk = clamp_score(1 + omitted_count + max(0, 2 - quantified_bullets))

    revision_target = choose_revision_target_stage(
        fit_score=fit_score,
        evidence_score=evidence_score,
        specificity_score=specificity_score,
        overstatement_risk=overstatement_risk,
        omitted_count=omitted_count,
    )
    overall_score = clamp_score(
        round(
            (
                fit_score
                + evidence_score
                + specificity_score
                + (6 - overstatement_risk)
            )
            / 4
        )
    )
    needs_revision = (
        fit_score <= 3
        or evidence_score <= 3
        or specificity_score <= 3
        or overstatement_risk >= 4
    )

    return EvaluationScorecardRecord(
        fit=EvaluationDimensionRecord(
            score=fit_score,
            rationale="Measures how many top JD requirements are explicitly reflected in the draft.",
            evidence=build_fit_evidence(analysis.top_requirements, resume_text),
        ),
        evidenceSupport=EvaluationDimensionRecord(
            score=evidence_score,
            rationale="Measures how much approved, draft-safe evidence survives into the final one-page package.",
            evidence=[
                f"{bullet_count} draft-safe bullets selected.",
                f"{omitted_count} top requirements remain omitted.",
            ],
        ),
        specificity=EvaluationDimensionRecord(
            score=specificity_score,
            rationale="Measures how concrete the bullets are via metrics, implementation details, or named systems.",
            evidence=[
                f"{quantified_bullets} of {bullet_count} selected bullets include measurable or concrete signals.",
            ],
        ),
        overstatementRisk=EvaluationDimensionRecord(
            score=overstatement_risk,
            rationale="Measures whether the draft overreaches beyond its strongest evidence base.",
            evidence=[
                f"{omitted_count} requirements are still thin or missing.",
                "Risk rises when the narrative claims more breadth than the selected evidence supports.",
            ],
        ),
        overallScore=overall_score,
        needsRevision=needs_revision,
        revisionTargetStage=revision_target,
        revisionSummary=build_revision_summary(
            fit_score=fit_score,
            evidence_score=evidence_score,
            specificity_score=specificity_score,
            overstatement_risk=overstatement_risk,
            revision_target=revision_target,
        ),
    )


def build_fit_evidence(requirements: list[str], resume_text: str) -> list[str]:
    evidence: list[str] = []
    for requirement in requirements:
        matched = all(token in resume_text for token in tokenize(requirement))
        evidence.append(
            f"{'Matched' if matched else 'Missing'}: {requirement}"
        )
    return evidence


def count_requirement_hits(requirements: list[str], resume_text: str) -> int:
    return sum(
        1
        for requirement in requirements
        if all(token in resume_text for token in tokenize(requirement))
    )


def choose_revision_target_stage(
    *,
    fit_score: int,
    evidence_score: int,
    specificity_score: int,
    overstatement_risk: int,
    omitted_count: int,
) -> StageKey:
    if overstatement_risk >= 4 or evidence_score <= 2 or omitted_count >= 2:
        return StageKey.CAREER_INTAKE
    if fit_score <= 3 or specificity_score <= 3:
        return StageKey.BLUEPRINT_REVIEW
    return StageKey.DRAFT_REVIEW


def build_revision_summary(
    *,
    fit_score: int,
    evidence_score: int,
    specificity_score: int,
    overstatement_risk: int,
    revision_target: StageKey,
) -> str:
    return (
        "Fit={fit}, evidence={evidence}, specificity={specificity}, "
        "overstatement risk={risk}. Rerun from {stage} if the user requests a targeted revision."
    ).format(
        fit=fit_score,
        evidence=evidence_score,
        specificity=specificity_score,
        risk=overstatement_risk,
        stage=revision_target.value,
    )


def has_metric(text: str) -> bool:
    return bool(re.search(r"\b\d[\d,.%+kKmM]*\b", text))


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in text.lower().replace("/", " ").replace("-", " ").split()
        if token and len(token) > 2
    ]


def clamp_score(value: int) -> int:
    return max(1, min(5, value))
