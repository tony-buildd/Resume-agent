from __future__ import annotations

import re
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AppUser
from app.orchestration.contracts import (
    InterrogationPromptRecord,
    JDAnalysisRecord,
    ResearchSummaryRecord,
)
from app.vault.retrieval import build_role_haystack, retrieve_vault_context


def build_interrogation_prompt(
    db: Session,
    *,
    user: AppUser,
    analysis: JDAnalysisRecord,
    research: ResearchSummaryRecord,
) -> InterrogationPromptRecord:
    query = " ".join(analysis.top_requirements[:5]) or analysis.primary_focus
    vault_context = retrieve_vault_context(
        db,
        user=user,
        query=query,
        limit=3,
        include_semantic=True,
    )

    target_requirement, coverage_score = select_requirement_gap(
        analysis=analysis,
        questioning_safe_roles=vault_context.questioning_safe_roles,
    )

    evidence_gap = (
        "The current vault does not show a concrete example for this requirement yet."
        if coverage_score == 0
        else "The vault has related context, but it still lacks enough concrete scope, metric, or ownership detail."
    )

    prompt = (
        f"What is the strongest example from your background that proves {target_requirement.lower()}? "
        "Include what you personally built, the stack, and what changed because of your work."
    )
    why_it_matters = (
        f"This role appears to prioritize {target_requirement.lower()}, and the current context still leaves "
        "a credibility gap the resume would need to close."
    )

    supporting_signals = [
        f"Primary focus: {analysis.primary_focus}",
        f"Archetype: {analysis.engineering_archetype}",
        *research.market_signals[:2],
    ]
    if vault_context.semantic_matches:
        supporting_signals.append(
            "Semantic vault recall found related notes, but not enough approved evidence."
        )

    return InterrogationPromptRecord(
        prompt=prompt,
        whyItMatters=why_it_matters,
        responseKey=build_response_key(target_requirement),
        targetRequirement=target_requirement,
        evidenceGap=evidence_gap,
        supportingSignals=supporting_signals,
    )


def build_canonical_session_context(
    runtime: dict[str, Any],
    *,
    prompt: InterrogationPromptRecord,
    answer: str,
) -> dict[str, dict[str, str]]:
    existing = dict(runtime.get("canonical_session_context") or {})
    existing[prompt.response_key] = {
        "targetRequirement": prompt.target_requirement,
        "whyItMatters": prompt.why_it_matters,
        "answer": answer,
    }
    return existing


def select_requirement_gap(
    *,
    analysis: JDAnalysisRecord,
    questioning_safe_roles: list[Any],
) -> tuple[str, int]:
    best_requirement = (
        analysis.top_requirements[0]
        if analysis.top_requirements
        else analysis.primary_focus
    )
    best_score = 10**9

    for requirement in analysis.top_requirements or [analysis.primary_focus]:
        score = sum(
            score_requirement_match(requirement, role)
            for role in questioning_safe_roles
        )
        if score < best_score:
            best_requirement = requirement
            best_score = score

    return best_requirement, best_score if best_score != 10**9 else 0


def score_requirement_match(requirement: str, role: Any) -> int:
    haystack = build_role_haystack(role)
    terms = [term for term in tokenize_requirement(requirement) if term]
    return sum(haystack.count(term) for term in terms)


def tokenize_requirement(value: str) -> list[str]:
    return re.findall(r"[a-z0-9/+.#-]{3,}", value.lower())


def build_response_key(requirement: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", requirement.lower()).strip("_")
    return f"gap_{slug[:40]}" or "gap_primary_requirement"
