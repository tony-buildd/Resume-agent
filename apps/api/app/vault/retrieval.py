from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.db.models import AppUser
from app.vault.contracts import (
    VaultBulletCandidateRecord,
    VaultFactRecord,
    VaultProjectStoryRecord,
    VaultRetrievalResponse,
    VaultRetrievalTraceRecord,
    VaultRoleRecord,
    VaultSemanticMatchRecord,
)
from app.vault.indexing import VaultIndexer
from app.vault.safety import is_draft_safe, is_questioning_safe
from app.vault.service import list_vault_roles, serialize_vault_role


def retrieve_vault_context(
    db: Session,
    *,
    user: AppUser,
    query: str | None = None,
    limit: int = 5,
    story_limit: int = 2,
    evidence_limit: int = 3,
    include_semantic: bool = True,
    indexer: VaultIndexer | None = None,
) -> VaultRetrievalResponse:
    roles = [serialize_vault_role(item) for item in list_vault_roles(db, user=user)]
    terms = tokenize_query(query)
    ranked_roles = rank_roles(roles, terms=terms)

    draft_safe_role_results = filter_none(
        filter_role(
            role,
            role_score=score,
            require_draft_eligible=True,
            safety_mode="draft",
            terms=terms,
            story_limit=story_limit,
            evidence_limit=evidence_limit,
        )
        for role, score in ranked_roles
    )
    questioning_safe_role_results = filter_none(
        filter_role(
            role,
            role_score=score,
            require_draft_eligible=False,
            safety_mode="questioning",
            terms=terms,
            story_limit=story_limit,
            evidence_limit=evidence_limit,
        )
        for role, score in ranked_roles
    )

    draft_safe_roles = [role for role, _ in draft_safe_role_results[:limit]]
    questioning_safe_roles = [role for role, _ in questioning_safe_role_results[:limit]]
    selection_traces = [
        trace
        for _, traces in draft_safe_role_results
        for trace in traces
    ] + [
        trace
        for _, traces in questioning_safe_role_results
        for trace in traces
    ]

    semantic_matches: list[VaultSemanticMatchRecord] = []
    if include_semantic and query:
        chroma = indexer or VaultIndexer()
        semantic_matches = [
            VaultSemanticMatchRecord(
                id=match.id,
                document=match.document,
                metadata=match.metadata,
                distance=match.distance,
            )
            for match in chroma.query(user_id=user.id, query_text=query, limit=limit)
        ]

    return VaultRetrievalResponse(
        query=query,
        draftSafeRoles=draft_safe_roles,
        questioningSafeRoles=questioning_safe_roles,
        semanticMatches=semantic_matches,
        selectionTraces=selection_traces,
    )


def filter_role(
    role: VaultRoleRecord,
    *,
    role_score: int,
    require_draft_eligible: bool,
    safety_mode: str,
    terms: list[str],
    story_limit: int,
    evidence_limit: int,
) -> tuple[VaultRoleRecord, list[VaultRetrievalTraceRecord]] | None:
    role_facts = rank_facts(
        role.role_facts,
        require_draft_eligible=require_draft_eligible,
        safety_mode=safety_mode,
        terms=terms,
        limit=evidence_limit,
    )
    role_bullets = rank_bullets(
        role.role_bullet_candidates,
        require_draft_eligible=require_draft_eligible,
        safety_mode=safety_mode,
        terms=terms,
        limit=evidence_limit,
    )

    project_stories: list[VaultProjectStoryRecord] = []
    traces: list[VaultRetrievalTraceRecord] = []
    story_rankings = rank_stories(role.project_stories, terms=terms)

    for story, story_score in story_rankings:
        story_facts = rank_facts(
            story.facts,
            require_draft_eligible=require_draft_eligible,
            safety_mode=safety_mode,
            terms=terms,
            limit=evidence_limit,
        )
        story_bullets = rank_bullets(
            story.bullet_candidates,
            require_draft_eligible=require_draft_eligible,
            safety_mode=safety_mode,
            terms=terms,
            limit=evidence_limit,
        )
        if not story_facts and not story_bullets:
            traces.append(
                build_trace(
                    mode=safety_mode,
                    level="story",
                    item_id=story.id,
                    parent_id=role.id,
                    label=story.name,
                    score=story_score,
                    selected=False,
                    reason="No evidence remained after safety filtering.",
                )
            )
            continue
        if len(project_stories) >= story_limit:
            traces.append(
                build_trace(
                    mode=safety_mode,
                    level="story",
                    item_id=story.id,
                    parent_id=role.id,
                    label=story.name,
                    score=story_score,
                    selected=False,
                    reason="Outside the active story shortlist budget.",
                )
            )
            continue

        project_stories.append(
            story.model_copy(
                update={
                    "facts": story_facts,
                    "bullet_candidates": story_bullets,
                }
            )
        )
        traces.append(
            build_trace(
                mode=safety_mode,
                level="story",
                item_id=story.id,
                parent_id=role.id,
                label=story.name,
                score=story_score,
                selected=True,
                reason="Selected into the story shortlist.",
            )
        )
        traces.extend(
            build_evidence_traces(
                story_facts,
                parent_id=story.id,
                level="fact",
                mode=safety_mode,
                terms=terms,
            )
        )
        traces.extend(
            build_evidence_traces(
                story_bullets,
                parent_id=story.id,
                level="bullet",
                mode=safety_mode,
                terms=terms,
            )
        )

    if not role_facts and not role_bullets and not project_stories:
        traces.append(
            build_trace(
                mode=safety_mode,
                level="role",
                item_id=role.id,
                parent_id=None,
                label=f"{role.title} @ {role.company.name}",
                score=role_score,
                selected=False,
                reason="No role-level or story-level evidence survived selection.",
            )
        )
        return None

    traces.append(
        build_trace(
            mode=safety_mode,
            level="role",
            item_id=role.id,
            parent_id=None,
            label=f"{role.title} @ {role.company.name}",
            score=role_score,
            selected=True,
            reason="Selected into the role shortlist.",
        )
    )
    traces.extend(
        build_evidence_traces(
            role_facts,
            parent_id=role.id,
            level="role_fact",
            mode=safety_mode,
            terms=terms,
        )
    )
    traces.extend(
        build_evidence_traces(
            role_bullets,
            parent_id=role.id,
            level="role_bullet",
            mode=safety_mode,
            terms=terms,
        )
    )

    return (
        role.model_copy(
            update={
                "role_facts": role_facts,
                "role_bullet_candidates": role_bullets,
                "project_stories": project_stories,
            }
        ),
        traces,
    )


def rank_facts(
    facts: Iterable[VaultFactRecord],
    *,
    require_draft_eligible: bool,
    safety_mode: str,
    terms: list[str],
    limit: int,
) -> list[VaultFactRecord]:
    allowed = [
        fact
        for fact in facts
        if (
            is_draft_safe(fact)
            if safety_mode == "draft"
            else is_questioning_safe(fact)
        )
        and (fact.draft_eligible or not require_draft_eligible)
    ]
    ranked = sorted(
        allowed,
        key=lambda fact: score_text(
            " ".join(
                part for part in [fact.kind, fact.statement, fact.evidence or ""] if part
            ),
            terms,
        ),
        reverse=True,
    )
    return ranked[:limit]


def rank_bullets(
    bullets: Iterable[VaultBulletCandidateRecord],
    *,
    require_draft_eligible: bool,
    safety_mode: str,
    terms: list[str],
    limit: int,
) -> list[VaultBulletCandidateRecord]:
    allowed = [
        bullet
        for bullet in bullets
        if (
            is_draft_safe(bullet)
            if safety_mode == "draft"
            else is_questioning_safe(bullet)
        )
        and (bullet.draft_eligible or not require_draft_eligible)
    ]
    ranked = sorted(
        allowed,
        key=lambda bullet: score_text(
            " ".join(part for part in [bullet.text, bullet.story_angle or ""] if part),
            terms,
        ),
        reverse=True,
    )
    return ranked[:limit]


def rank_roles(
    roles: list[VaultRoleRecord],
    *,
    terms: list[str],
) -> list[tuple[VaultRoleRecord, int]]:
    if not terms:
        return [(role, 1) for role in roles]

    ranked = sorted(
        ((role, score_role(role, terms)) for role in roles),
        key=lambda item: item[1],
        reverse=True,
    )
    return [item for item in ranked if item[1] > 0]


def rank_stories(
    stories: Iterable[VaultProjectStoryRecord],
    *,
    terms: list[str],
) -> list[tuple[VaultProjectStoryRecord, int]]:
    ranked = [
        (
            story,
            score_text(
                " ".join(
                    part
                    for part in [
                        story.name,
                        story.summary or "",
                        story.stack_summary or "",
                        story.impact_summary or "",
                        *(fact.statement for fact in story.facts),
                        *(bullet.text for bullet in story.bullet_candidates),
                    ]
                    if part
                ),
                terms,
            ),
        )
        for story in stories
    ]
    return sorted(ranked, key=lambda item: item[1], reverse=True)


def score_role(role: VaultRoleRecord, terms: list[str]) -> int:
    return score_text(build_role_haystack(role), terms)


def build_role_haystack(role: VaultRoleRecord) -> str:
    parts = [
        role.company.name,
        role.title,
        role.summary or "",
        *(fact.statement for fact in role.role_facts),
        *(bullet.text for bullet in role.role_bullet_candidates),
    ]
    for story in role.project_stories:
        parts.extend(
            [
                story.name,
                story.summary or "",
                story.stack_summary or "",
                story.impact_summary or "",
                *(fact.statement for fact in story.facts),
                *(bullet.text for bullet in story.bullet_candidates),
            ]
        )
    return " ".join(parts).lower()


def build_evidence_traces(
    items: Iterable[VaultFactRecord | VaultBulletCandidateRecord],
    *,
    parent_id: str,
    level: str,
    mode: str,
    terms: list[str],
) -> list[VaultRetrievalTraceRecord]:
    traces: list[VaultRetrievalTraceRecord] = []
    for item in items:
        label = item.statement if isinstance(item, VaultFactRecord) else item.text
        traces.append(
            build_trace(
                mode=mode,
                level=level,
                item_id=item.id,
                parent_id=parent_id,
                label=label,
                score=score_text(label, terms),
                selected=True,
                reason="Selected as evidence for the current shortlist level.",
            )
        )
    return traces


def build_trace(
    *,
    mode: str,
    level: str,
    item_id: str | None,
    parent_id: str | None,
    label: str,
    score: int,
    selected: bool,
    reason: str,
) -> VaultRetrievalTraceRecord:
    return VaultRetrievalTraceRecord(
        mode=mode,
        level=level,
        itemId=item_id,
        parentId=parent_id,
        label=label,
        score=score,
        selected=selected,
        reason=reason,
    )


def score_text(text: str, terms: list[str]) -> int:
    haystack = text.lower()
    if not terms:
        return 1 if haystack else 0
    return sum(haystack.count(term) for term in terms)


def tokenize_query(query: str | None) -> list[str]:
    if not query:
        return []
    return [item for item in query.lower().split() if item]


def filter_none[T](items: Iterable[T | None]) -> list[T]:
    return [item for item in items if item is not None]
