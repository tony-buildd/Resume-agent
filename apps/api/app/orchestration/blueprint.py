from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.db.models import AppUser
from app.orchestration.contracts import (
    BlueprintBulletRecord,
    BlueprintRoleRecord,
    BlueprintSectionRecord,
    JDAnalysisRecord,
    NarrativeBlueprintRecord,
    ResearchSummaryRecord,
)
from app.vault.contracts import (
    VaultBulletCandidateRecord,
    VaultProjectStoryRecord,
    VaultRetrievalResponse,
    VaultRoleRecord,
)
from app.vault.retrieval import build_role_haystack, retrieve_vault_context

MAX_ROLES = 2
MAX_BULLETS_PER_ROLE = 3
MAX_PROJECTS = 1


def build_narrative_blueprint(
    db: Session,
    *,
    user: AppUser,
    analysis: JDAnalysisRecord,
    research: ResearchSummaryRecord,
    canonical_context: dict[str, object],
) -> NarrativeBlueprintRecord:
    keyword_priorities = collect_keyword_priorities(analysis)
    retrieval = retrieve_vault_context(
        db,
        user=user,
        query=build_blueprint_query(analysis, research, canonical_context),
        limit=MAX_ROLES + 1,
        include_semantic=False,
    )
    selected_roles = select_roles(retrieval, keyword_priorities)
    matched_terms = collect_matched_terms(selected_roles, keyword_priorities)

    return NarrativeBlueprintRecord(
        narrativeAngle=build_narrative_angle(analysis, research, selected_roles),
        headlineFocus=build_headline_focus(analysis, research),
        keywordPriorities=keyword_priorities,
        skillsFocus=select_skills_focus(keyword_priorities, selected_roles),
        selectedRoles=selected_roles,
        sections=build_sections(selected_roles),
        omittedSignals=[
            requirement
            for requirement in analysis.top_requirements
            if not requirement_matches(requirement, matched_terms)
        ],
        onePageStrategy=(
            "Lead with the strongest JD-aligned bullets, keep experience to two roles max, "
            "and cut any story that does not add direct evidence for the target role."
        ),
    )


def build_blueprint_query(
    analysis: JDAnalysisRecord,
    research: ResearchSummaryRecord,
    canonical_context: dict[str, object],
) -> str:
    parts = [
        *analysis.top_requirements,
        *analysis.repeating_terms,
        analysis.primary_focus,
        analysis.engineering_archetype,
        research.role_title or "",
        research.company_name or "",
        research.strategic_summary,
        *(str(value) for value in canonical_context.values()),
    ]
    return " ".join(part for part in parts if part).strip()


def select_roles(
    retrieval: VaultRetrievalResponse,
    keyword_priorities: list[str],
) -> list[BlueprintRoleRecord]:
    selected_roles: list[BlueprintRoleRecord] = []

    for role in retrieval.draft_safe_roles[:MAX_ROLES]:
        bullets = select_role_bullets(role, keyword_priorities)
        if not bullets:
            continue

        selected_roles.append(
            BlueprintRoleRecord(
                roleId=role.id,
                companyName=role.company.name,
                roleTitle=role.title,
                whySelected=build_role_rationale(role, bullets, keyword_priorities),
                selectedBullets=bullets,
                selectedStoryNames=collect_story_names(bullets),
            )
        )

    return selected_roles


def select_role_bullets(
    role: VaultRoleRecord,
    keyword_priorities: list[str],
) -> list[BlueprintBulletRecord]:
    ranked_candidates: list[tuple[int, BlueprintBulletRecord]] = []

    for bullet in role.role_bullet_candidates:
        ranked_candidates.append(
            (
                score_text(bullet.text, keyword_priorities),
                BlueprintBulletRecord(
                    bulletId=bullet.id,
                    text=bullet.text,
                    rationale=build_bullet_rationale(bullet.text, keyword_priorities),
                ),
            )
        )

    story_count = 0
    for story in rank_stories(role.project_stories, keyword_priorities):
        if story_count >= MAX_PROJECTS:
            break
        story_count += 1
        for bullet in story.bullet_candidates:
            ranked_candidates.append(
                (
                    score_text(bullet.text, keyword_priorities) + 1,
                    BlueprintBulletRecord(
                        bulletId=bullet.id,
                        text=bullet.text,
                        sourceStoryId=story.id,
                        sourceStoryName=story.name,
                        rationale=build_bullet_rationale(
                            bullet.text, keyword_priorities
                        ),
                    ),
                )
            )

    ranked_candidates.sort(key=lambda item: item[0], reverse=True)
    unique: list[BlueprintBulletRecord] = []
    seen_texts: set[str] = set()
    for _, bullet in ranked_candidates:
        key = bullet.text.strip().lower()
        if not key or key in seen_texts:
            continue
        unique.append(bullet)
        seen_texts.add(key)
        if len(unique) >= MAX_BULLETS_PER_ROLE:
            break

    return unique


def rank_stories(
    stories: Iterable[VaultProjectStoryRecord],
    keyword_priorities: list[str],
) -> list[VaultProjectStoryRecord]:
    return sorted(
        stories,
        key=lambda story: score_text(
            " ".join(
                part
                for part in [
                    story.name,
                    story.summary or "",
                    story.stack_summary or "",
                    story.impact_summary or "",
                    *(bullet.text for bullet in story.bullet_candidates),
                ]
                if part
            ),
            keyword_priorities,
        ),
        reverse=True,
    )


def build_narrative_angle(
    analysis: JDAnalysisRecord,
    research: ResearchSummaryRecord,
    roles: list[BlueprintRoleRecord],
) -> str:
    if roles:
        lead = roles[0]
        return (
            f"Frame the candidate as a {analysis.engineering_archetype.lower()} who can "
            f"deliver {analysis.primary_focus.lower()} outcomes, led by evidence from "
            f"{lead.role_title} at {lead.company_name}."
        )

    return (
        "Frame the candidate around the approved JD requirements first, but call out that "
        "more draft-safe evidence is still needed before the final story is credible."
    )


def build_headline_focus(
    analysis: JDAnalysisRecord,
    research: ResearchSummaryRecord,
) -> str:
    role_title = research.role_title or "target role"
    return f"Optimize the resume for {role_title} with emphasis on {analysis.primary_focus.lower()}."


def build_sections(
    selected_roles: list[BlueprintRoleRecord],
) -> list[BlueprintSectionRecord]:
    return [
        BlueprintSectionRecord(key="header", label="Header", included=True, maxItems=1),
        BlueprintSectionRecord(key="skills", label="Skills", included=True, maxItems=8),
        BlueprintSectionRecord(
            key="experience",
            label="Experience",
            included=bool(selected_roles),
            maxItems=MAX_ROLES,
        ),
        BlueprintSectionRecord(
            key="projects",
            label="Projects",
            included=any(role.selected_story_names for role in selected_roles),
            maxItems=MAX_PROJECTS,
        ),
    ]


def select_skills_focus(
    keyword_priorities: list[str],
    roles: list[BlueprintRoleRecord],
) -> list[str]:
    skills: list[str] = []
    for keyword in keyword_priorities:
        if len(skills) >= 8:
            break
        if any(keyword.lower() in role.why_selected.lower() for role in roles):
            skills.append(keyword)

    if skills:
        return skills

    return keyword_priorities[:8]


def build_role_rationale(
    role: VaultRoleRecord,
    bullets: list[BlueprintBulletRecord],
    keyword_priorities: list[str],
) -> str:
    matched = match_terms(build_role_haystack(role), keyword_priorities)
    sources = collect_story_names(bullets)
    source_text = f" with emphasis on {', '.join(sources)}" if sources else ""
    if matched:
        return (
            f"This role carries the strongest draft-safe evidence for {', '.join(matched[:3])}"
            f"{source_text}."
        )

    return (
        f"This role carries the strongest available draft-safe evidence{source_text}."
    )


def build_bullet_rationale(text: str, keyword_priorities: list[str]) -> str:
    matched = match_terms(text.lower(), keyword_priorities)
    if matched:
        return f"Supports {', '.join(matched[:2])}."
    return "Supports the broader narrative angle."


def collect_story_names(bullets: Iterable[BlueprintBulletRecord]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for bullet in bullets:
        if not bullet.source_story_name:
            continue
        key = bullet.source_story_name.lower()
        if key in seen:
            continue
        seen.add(key)
        names.append(bullet.source_story_name)
    return names


def collect_keyword_priorities(analysis: JDAnalysisRecord) -> list[str]:
    ordered: list[str] = []
    for item in [*analysis.top_requirements, *analysis.repeating_terms]:
        normalized = item.strip()
        if not normalized:
            continue
        if normalized.lower() in {value.lower() for value in ordered}:
            continue
        ordered.append(normalized)
    return ordered[:10]


def collect_matched_terms(
    roles: Iterable[BlueprintRoleRecord],
    keyword_priorities: list[str],
) -> set[str]:
    matched: set[str] = set()
    for role in roles:
        matched.update(match_terms(role.why_selected.lower(), keyword_priorities))
        for bullet in role.selected_bullets:
            matched.update(match_terms(bullet.text.lower(), keyword_priorities))
    return matched


def requirement_matches(requirement: str, matched_terms: set[str]) -> bool:
    requirement_terms = {token for token in tokenize(requirement) if len(token) > 2}
    return any(term in matched_terms for term in requirement_terms)


def score_text(text: str, keyword_priorities: list[str]) -> int:
    haystack = text.lower()
    score = 0
    for term in keyword_priorities:
        term_tokens = tokenize(term)
        if all(token in haystack for token in term_tokens):
            score += 3
        score += sum(haystack.count(token) for token in term_tokens)
    return score


def match_terms(text: str, keyword_priorities: list[str]) -> list[str]:
    matched: list[str] = []
    haystack = text.lower()
    for term in keyword_priorities:
        if all(token in haystack for token in tokenize(term)):
            matched.append(term.lower())
    return matched


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in text.lower().replace("/", " ").replace("-", " ").split()
        if token
    ]
