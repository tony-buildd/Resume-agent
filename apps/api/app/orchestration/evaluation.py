from __future__ import annotations

import re

from app.orchestration.contracts import (
    EvaluationDimensionKey,
    EvaluationDimensionRecord,
    EvaluationRubricDimensionRecord,
    EvaluationRubricRecord,
    EvaluationScorecardRecord,
    JDAnalysisRecord,
    NarrativeBlueprintRecord,
    ResumePackageRecord,
    StageKey,
)

SYSTEMS_TERMS = {
    "backend",
    "platform",
    "infra",
    "infrastructure",
    "performance",
    "distributed",
    "reliability",
    "data",
}
PRODUCT_TERMS = {"frontend", "product", "ui", "ux", "customer", "design"}
CAREER_SWITCH_TERMS = {"career switch", "switch", "adjacent", "stretch"}

BASE_WEIGHT_MAP: dict[EvaluationDimensionKey, float] = {
    EvaluationDimensionKey.JD_FIT: 1.2,
    EvaluationDimensionKey.EVIDENCE_SUPPORT: 1.1,
    EvaluationDimensionKey.EVIDENCE_COVERAGE: 1.0,
    EvaluationDimensionKey.SPECIFICITY: 1.0,
    EvaluationDimensionKey.OVERSTATEMENT_RISK: 1.2,
}

DIMENSION_LABELS: dict[EvaluationDimensionKey, str] = {
    EvaluationDimensionKey.JD_FIT: "JD fit",
    EvaluationDimensionKey.EVIDENCE_SUPPORT: "Evidence support",
    EvaluationDimensionKey.EVIDENCE_COVERAGE: "Evidence coverage",
    EvaluationDimensionKey.SPECIFICITY: "Specificity",
    EvaluationDimensionKey.OVERSTATEMENT_RISK: "Overstatement risk",
}


def evaluate_resume_package(
    *,
    blueprint: NarrativeBlueprintRecord,
    package: ResumePackageRecord,
    analysis: JDAnalysisRecord,
) -> EvaluationScorecardRecord:
    resume_text = package.markdown_resume.lower()
    bullets = [
        bullet for role in blueprint.selected_roles for bullet in role.selected_bullets
    ]
    bullet_count = max(len(bullets), 1)
    quantified_bullets = sum(1 for bullet in bullets if has_metric(bullet.text))
    covered_requirements = count_requirement_hits(
        analysis.top_requirements,
        resume_text,
    )
    total_requirements = max(len(analysis.top_requirements), 1)
    omitted_count = len(blueprint.omitted_signals)
    selected_role_count = max(len(blueprint.selected_roles), 1)
    selected_story_count = sum(
        max(len(role.selected_story_names), 1 if role.selected_bullets else 0)
        for role in blueprint.selected_roles
    )
    role_coverage_ratio = min(selected_story_count / selected_role_count, 1.0)
    requirement_coverage_ratio = covered_requirements / total_requirements

    profile, focus, weighting_rationale = choose_rubric_profile(analysis, blueprint)
    weight_map = build_weight_map(profile)
    rubric = build_rubric_record(
        profile=profile,
        focus=focus,
        weight_map=weight_map,
        weighting_rationale=weighting_rationale,
    )

    fit_score = clamp_score(round(requirement_coverage_ratio * 5))
    evidence_score = clamp_score(
        round(((bullet_count - omitted_count) / bullet_count) * 5)
    )
    evidence_coverage_score = clamp_score(
        round(((requirement_coverage_ratio + role_coverage_ratio) / 2) * 5)
    )
    specificity_score = clamp_score(round((quantified_bullets / bullet_count) * 5))
    overstatement_risk = clamp_score(
        1 + omitted_count + max(0, 2 - quantified_bullets)
    )

    fit_dimension = EvaluationDimensionRecord(
        key=EvaluationDimensionKey.JD_FIT,
        label=DIMENSION_LABELS[EvaluationDimensionKey.JD_FIT],
        weight=weight_map[EvaluationDimensionKey.JD_FIT],
        score=fit_score,
        rationale="Measures how directly the draft mirrors the highest-value job requirements.",
        evidence=build_fit_evidence(analysis.top_requirements, resume_text),
    )
    evidence_support_dimension = EvaluationDimensionRecord(
        key=EvaluationDimensionKey.EVIDENCE_SUPPORT,
        label=DIMENSION_LABELS[EvaluationDimensionKey.EVIDENCE_SUPPORT],
        weight=weight_map[EvaluationDimensionKey.EVIDENCE_SUPPORT],
        score=evidence_score,
        rationale="Measures how much approved, draft-safe evidence survives into the final one-page package.",
        evidence=[
            f"{bullet_count} draft-safe bullets selected across {selected_role_count} roles.",
            f"{omitted_count} top requirements remain thin or omitted.",
        ],
    )
    evidence_coverage_dimension = EvaluationDimensionRecord(
        key=EvaluationDimensionKey.EVIDENCE_COVERAGE,
        label=DIMENSION_LABELS[EvaluationDimensionKey.EVIDENCE_COVERAGE],
        weight=weight_map[EvaluationDimensionKey.EVIDENCE_COVERAGE],
        score=evidence_coverage_score,
        rationale="Measures whether the selected evidence covers both the JD surface area and enough distinct role/story context.",
        evidence=[
            f"{covered_requirements} of {total_requirements} top requirements are explicitly represented.",
            f"{selected_story_count} story threads contributed evidence across {selected_role_count} selected roles.",
        ],
    )
    specificity_dimension = EvaluationDimensionRecord(
        key=EvaluationDimensionKey.SPECIFICITY,
        label=DIMENSION_LABELS[EvaluationDimensionKey.SPECIFICITY],
        weight=weight_map[EvaluationDimensionKey.SPECIFICITY],
        score=specificity_score,
        rationale="Measures how concrete the bullets are via metrics, named systems, or implementation details.",
        evidence=[
            f"{quantified_bullets} of {bullet_count} selected bullets include measurable or concrete signals.",
        ],
    )
    overstatement_dimension = EvaluationDimensionRecord(
        key=EvaluationDimensionKey.OVERSTATEMENT_RISK,
        label=DIMENSION_LABELS[EvaluationDimensionKey.OVERSTATEMENT_RISK],
        weight=weight_map[EvaluationDimensionKey.OVERSTATEMENT_RISK],
        score=overstatement_risk,
        rationale="Measures whether the narrative claims more breadth than the evidence base currently supports.",
        evidence=[
            f"{omitted_count} top requirements remain under-supported.",
            "Risk increases when breadth grows faster than validated evidence density.",
        ],
    )

    dimensions = [
        fit_dimension,
        evidence_support_dimension,
        evidence_coverage_dimension,
        specificity_dimension,
        overstatement_dimension,
    ]
    overall_score = calculate_weighted_overall_score(dimensions)
    revision_target = choose_revision_target_stage(
        fit_score=fit_score,
        evidence_score=evidence_score,
        evidence_coverage_score=evidence_coverage_score,
        specificity_score=specificity_score,
        overstatement_risk=overstatement_risk,
        omitted_count=omitted_count,
    )
    needs_revision = (
        fit_score <= 3
        or evidence_score <= 3
        or evidence_coverage_score <= 3
        or specificity_score <= 3
        or overstatement_risk >= 4
    )

    return EvaluationScorecardRecord(
        rubric=rubric,
        dimensions=dimensions,
        fit=fit_dimension,
        evidenceSupport=evidence_support_dimension,
        specificity=specificity_dimension,
        overstatementRisk=overstatement_dimension,
        overallScore=overall_score,
        needsRevision=needs_revision,
        revisionTargetStage=revision_target,
        revisionSummary=build_revision_summary(
            profile=profile,
            fit_score=fit_score,
            evidence_score=evidence_score,
            evidence_coverage_score=evidence_coverage_score,
            specificity_score=specificity_score,
            overstatement_risk=overstatement_risk,
            revision_target=revision_target,
        ),
    )


def build_rubric_record(
    *,
    profile: str,
    focus: str,
    weight_map: dict[EvaluationDimensionKey, float],
    weighting_rationale: str,
) -> EvaluationRubricRecord:
    return EvaluationRubricRecord(
        profile=profile,
        focus=focus,
        weightingRationale=weighting_rationale,
        dimensions=[
            EvaluationRubricDimensionRecord(
                key=key,
                label=DIMENSION_LABELS[key],
                weight=weight_map[key],
                emphasis=build_emphasis(profile, key),
            )
            for key in (
                EvaluationDimensionKey.JD_FIT,
                EvaluationDimensionKey.EVIDENCE_SUPPORT,
                EvaluationDimensionKey.EVIDENCE_COVERAGE,
                EvaluationDimensionKey.SPECIFICITY,
                EvaluationDimensionKey.OVERSTATEMENT_RISK,
            )
        ],
    )


def build_weight_map(profile: str) -> dict[EvaluationDimensionKey, float]:
    weights = dict(BASE_WEIGHT_MAP)

    if profile == "systems":
        weights[EvaluationDimensionKey.EVIDENCE_SUPPORT] = 1.3
        weights[EvaluationDimensionKey.EVIDENCE_COVERAGE] = 1.25
        weights[EvaluationDimensionKey.SPECIFICITY] = 1.15
    elif profile == "product":
        weights[EvaluationDimensionKey.JD_FIT] = 1.25
        weights[EvaluationDimensionKey.SPECIFICITY] = 1.2
        weights[EvaluationDimensionKey.OVERSTATEMENT_RISK] = 1.15
    elif profile == "career-switch":
        weights[EvaluationDimensionKey.EVIDENCE_SUPPORT] = 1.25
        weights[EvaluationDimensionKey.OVERSTATEMENT_RISK] = 1.35
        weights[EvaluationDimensionKey.JD_FIT] = 1.1

    return weights


def choose_rubric_profile(
    analysis: JDAnalysisRecord,
    blueprint: NarrativeBlueprintRecord,
) -> tuple[str, str, str]:
    focus = " ".join(
        [
            analysis.primary_focus.lower(),
            analysis.engineering_archetype.lower(),
            blueprint.headline_focus.lower(),
            blueprint.narrative_angle.lower(),
        ]
    )

    if any(term in focus for term in CAREER_SWITCH_TERMS):
        return (
            "career-switch",
            "credibility and transferability",
            "This rubric leans harder on supported evidence and conservative claims because the narrative signals an adjacent or stretch positioning.",
        )
    if any(term in focus for term in SYSTEMS_TERMS):
        return (
            "systems",
            "systems evidence and implementation depth",
            "This rubric weights evidence density and technical specificity more heavily because the role emphasis is backend, platform, data, or infrastructure oriented.",
        )
    if any(term in focus for term in PRODUCT_TERMS):
        return (
            "product",
            "user impact and ownership clarity",
            "This rubric weights direct JD fit and specificity more heavily because the role emphasis is frontend or product-oriented.",
        )
    return (
        "generalist",
        "balanced role fit and evidence quality",
        "This rubric keeps a balanced weighting because the role reads as multi-surface rather than strongly specialized.",
    )


def build_emphasis(profile: str, key: EvaluationDimensionKey) -> str:
    if profile == "systems" and key in {
        EvaluationDimensionKey.EVIDENCE_SUPPORT,
        EvaluationDimensionKey.EVIDENCE_COVERAGE,
        EvaluationDimensionKey.SPECIFICITY,
    }:
        return "High"
    if profile == "product" and key in {
        EvaluationDimensionKey.JD_FIT,
        EvaluationDimensionKey.SPECIFICITY,
    }:
        return "High"
    if profile == "career-switch" and key in {
        EvaluationDimensionKey.EVIDENCE_SUPPORT,
        EvaluationDimensionKey.OVERSTATEMENT_RISK,
    }:
        return "High"
    return "Standard"


def calculate_weighted_overall_score(
    dimensions: list[EvaluationDimensionRecord],
) -> int:
    weighted_total = 0.0
    total_weight = 0.0
    for dimension in dimensions:
        weight = dimension.weight or 1.0
        score = dimension.score
        if dimension.key is EvaluationDimensionKey.OVERSTATEMENT_RISK:
            score = 6 - score
        weighted_total += score * weight
        total_weight += weight

    if total_weight <= 0:
        return 1
    return clamp_score(round(weighted_total / total_weight))


def build_fit_evidence(requirements: list[str], resume_text: str) -> list[str]:
    evidence: list[str] = []
    for requirement in requirements:
        matched = all(token in resume_text for token in tokenize(requirement))
        evidence.append(f"{'Matched' if matched else 'Missing'}: {requirement}")
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
    evidence_coverage_score: int,
    specificity_score: int,
    overstatement_risk: int,
    omitted_count: int,
) -> StageKey:
    if (
        overstatement_risk >= 4
        or evidence_score <= 2
        or evidence_coverage_score <= 2
        or omitted_count >= 2
    ):
        return StageKey.CAREER_INTAKE
    if fit_score <= 3 or specificity_score <= 3:
        return StageKey.BLUEPRINT_REVIEW
    return StageKey.DRAFT_REVIEW


def build_revision_summary(
    *,
    profile: str,
    fit_score: int,
    evidence_score: int,
    evidence_coverage_score: int,
    specificity_score: int,
    overstatement_risk: int,
    revision_target: StageKey,
) -> str:
    return (
        "Rubric={profile}. Fit={fit}, evidence={evidence}, coverage={coverage}, "
        "specificity={specificity}, overstatement risk={risk}. "
        "Rerun from {stage} for the next targeted revision."
    ).format(
        profile=profile,
        fit=fit_score,
        evidence=evidence_score,
        coverage=evidence_coverage_score,
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
