from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.db.models import AppUser, VaultReviewState
from app.vault.contracts import (
    VaultBulletCandidateRecord,
    VaultFactRecord,
    VaultProjectStoryRecord,
    VaultRetrievalResponse,
    VaultRoleRecord,
    VaultSemanticMatchRecord,
)
from app.vault.indexing import VaultIndexer
from app.vault.service import list_vault_roles, serialize_vault_role


DRAFT_SAFE_REVIEW_STATES = {
    VaultReviewState.USER_STATED,
    VaultReviewState.APPROVED,
}
QUESTIONING_SAFE_REVIEW_STATES = {
    VaultReviewState.USER_STATED,
    VaultReviewState.APPROVED,
    VaultReviewState.INFERRED,
}


def retrieve_vault_context(
    db: Session,
    *,
    user: AppUser,
    query: str | None = None,
    limit: int = 5,
    include_semantic: bool = True,
    indexer: VaultIndexer | None = None,
) -> VaultRetrievalResponse:
    roles = [serialize_vault_role(item) for item in list_vault_roles(db, user=user)]
    ranked_roles = rank_roles(roles, query=query, limit=limit)

    draft_safe_roles = filter_none(
        filter_role(
            role,
            allowed_review_states=DRAFT_SAFE_REVIEW_STATES,
            require_draft_eligible=True,
        )
        for role in ranked_roles
    )
    questioning_safe_roles = filter_none(
        filter_role(
            role,
            allowed_review_states=QUESTIONING_SAFE_REVIEW_STATES,
            require_draft_eligible=False,
        )
        for role in ranked_roles
    )

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
    )


def filter_role(
    role: VaultRoleRecord,
    *,
    allowed_review_states: set[VaultReviewState],
    require_draft_eligible: bool,
) -> VaultRoleRecord | None:
    role_facts = filter_facts(
        role.role_facts,
        allowed_review_states=allowed_review_states,
        require_draft_eligible=require_draft_eligible,
    )
    role_bullets = filter_bullets(
        role.role_bullet_candidates,
        allowed_review_states=allowed_review_states,
        require_draft_eligible=require_draft_eligible,
    )

    project_stories: list[VaultProjectStoryRecord] = []
    for story in role.project_stories:
        story_facts = filter_facts(
            story.facts,
            allowed_review_states=allowed_review_states,
            require_draft_eligible=require_draft_eligible,
        )
        story_bullets = filter_bullets(
            story.bullet_candidates,
            allowed_review_states=allowed_review_states,
            require_draft_eligible=require_draft_eligible,
        )
        if not story_facts and not story_bullets:
            continue

        project_stories.append(
            story.model_copy(
                update={
                    "facts": story_facts,
                    "bullet_candidates": story_bullets,
                }
            )
        )

    if not role_facts and not role_bullets and not project_stories:
        return None

    return role.model_copy(
        update={
            "role_facts": role_facts,
            "role_bullet_candidates": role_bullets,
            "project_stories": project_stories,
        }
    )


def filter_facts(
    facts: Iterable[VaultFactRecord],
    *,
    allowed_review_states: set[VaultReviewState],
    require_draft_eligible: bool,
) -> list[VaultFactRecord]:
    return [
        fact
        for fact in facts
        if fact.review_state in allowed_review_states
        and (fact.draft_eligible or not require_draft_eligible)
    ]


def filter_bullets(
    bullets: Iterable[VaultBulletCandidateRecord],
    *,
    allowed_review_states: set[VaultReviewState],
    require_draft_eligible: bool,
) -> list[VaultBulletCandidateRecord]:
    return [
        bullet
        for bullet in bullets
        if bullet.review_state in allowed_review_states
        and (bullet.draft_eligible or not require_draft_eligible)
    ]


def rank_roles(
    roles: list[VaultRoleRecord],
    *,
    query: str | None,
    limit: int,
) -> list[VaultRoleRecord]:
    if not query:
        return roles[:limit]

    terms = [item for item in query.lower().split() if item]
    ranked = sorted(
        roles,
        key=lambda role: score_role(role, terms),
        reverse=True,
    )
    return [role for role in ranked if score_role(role, terms) > 0][:limit]


def score_role(role: VaultRoleRecord, terms: list[str]) -> int:
    haystack = build_role_haystack(role)
    return sum(haystack.count(term) for term in terms)


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


def filter_none[T](items: Iterable[T | None]) -> list[T]:
    return [item for item in items if item is not None]
