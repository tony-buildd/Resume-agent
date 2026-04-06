from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    AppUser,
    VaultBulletCandidate,
    VaultCompany,
    VaultFact,
    VaultProjectStory,
    VaultRole,
)
from app.vault.contracts import (
    CreateVaultRoleRequest,
    VaultBulletCandidateInput,
    VaultBulletCandidateRecord,
    VaultCompanyRecord,
    VaultFactInput,
    VaultFactRecord,
    VaultProjectStoryInput,
    VaultProjectStoryRecord,
    VaultRoleRecord,
)
from app.vault.safety import hydrate_role_safety


def create_vault_role_tree(
    db: Session,
    *,
    user: AppUser,
    payload: CreateVaultRoleRequest,
) -> VaultRole:
    company = VaultCompany(
        user_id=user.id,
        name=payload.company_name,
        domain=payload.company_domain,
        summary=payload.company_summary,
    )
    role = VaultRole(
        title=payload.title,
        start_date=payload.start_date,
        end_date=payload.end_date,
        location=payload.location,
        employment_type=payload.employment_type,
        summary=payload.summary,
        details=payload.details,
    )
    company.roles.append(role)

    fact_lookup: dict[str, VaultFact] = {}

    for fact_input in payload.role_facts:
        fact = build_fact(role=role, project_story=None, payload=fact_input)
        fact_lookup[fact_input.client_key] = fact

    for bullet_input in payload.role_bullet_candidates:
        build_bullet(
            role=role,
            project_story=None,
            payload=bullet_input,
            fact_lookup=fact_lookup,
        )

    for story_input in payload.project_stories:
        story = VaultProjectStory(
            name=story_input.name,
            summary=story_input.summary,
            stack_summary=story_input.stack_summary,
            impact_summary=story_input.impact_summary,
            source_type=story_input.source_type,
            review_state=story_input.review_state,
            memory_tier=story_input.memory_tier,
            validation_status=story_input.validation_status,
            contamination_risk=story_input.contamination_risk,
            quarantine_reason=story_input.quarantine_reason,
            feasibility_checks=story_input.feasibility_checks,
            draft_eligible=story_input.draft_eligible,
            details=story_input.details,
        )
        role.project_stories.append(story)

        for fact_input in story_input.facts:
            fact = build_fact(role=role, project_story=story, payload=fact_input)
            fact_lookup[fact_input.client_key] = fact

        for bullet_input in story_input.bullet_candidates:
            build_bullet(
                role=role,
                project_story=story,
                payload=bullet_input,
                fact_lookup=fact_lookup,
            )

    db.add(company)
    hydrate_role_safety(role, company_name=company.name)
    db.flush()
    return role


def list_vault_roles(db: Session, *, user: AppUser) -> list[VaultRole]:
    records = db.scalars(
        base_vault_role_query()
        .join(VaultCompany)
        .where(VaultCompany.user_id == user.id)
    )
    return list(records)


def base_vault_role_query() -> Select[VaultRole]:
    return select(VaultRole).options(
        selectinload(VaultRole.company),
        selectinload(VaultRole.facts),
        selectinload(VaultRole.bullet_candidates).selectinload(
            VaultBulletCandidate.supporting_facts
        ),
        selectinload(VaultRole.project_stories).selectinload(VaultProjectStory.facts),
        selectinload(VaultRole.project_stories)
        .selectinload(VaultProjectStory.bullet_candidates)
        .selectinload(VaultBulletCandidate.supporting_facts),
    )


def serialize_vault_role(record: VaultRole) -> VaultRoleRecord:
    hydrate_role_safety(record, company_name=record.company.name)
    role_level_facts = [item for item in record.facts if item.project_story_id is None]
    role_level_bullets = [
        item for item in record.bullet_candidates if item.project_story_id is None
    ]
    return VaultRoleRecord(
        id=record.id,
        title=record.title,
        startDate=record.start_date,
        endDate=record.end_date,
        location=record.location,
        employmentType=record.employment_type,
        summary=record.summary,
        details=record.details,
        company=serialize_company(record.company),
        roleFacts=[serialize_fact(item) for item in role_level_facts],
        roleBulletCandidates=[serialize_bullet(item) for item in role_level_bullets],
        projectStories=[serialize_story(item) for item in record.project_stories],
        createdAt=record.created_at,
        updatedAt=record.updated_at,
    )


def serialize_company(record: VaultCompany) -> VaultCompanyRecord:
    return VaultCompanyRecord(
        id=record.id,
        name=record.name,
        domain=record.domain,
        summary=record.summary,
        details=record.details,
        createdAt=record.created_at,
        updatedAt=record.updated_at,
    )


def serialize_story(record: VaultProjectStory) -> VaultProjectStoryRecord:
    return VaultProjectStoryRecord(
        id=record.id,
        name=record.name,
        summary=record.summary,
        stackSummary=record.stack_summary,
        impactSummary=record.impact_summary,
        sourceType=record.source_type,
        reviewState=record.review_state,
        memoryTier=record.memory_tier,
        validationStatus=record.validation_status,
        contaminationRisk=record.contamination_risk,
        quarantineReason=record.quarantine_reason,
        feasibilityChecks=record.feasibility_checks,
        draftEligible=record.draft_eligible,
        details=record.details,
        facts=[serialize_fact(item) for item in record.facts],
        bulletCandidates=[serialize_bullet(item) for item in record.bullet_candidates],
        createdAt=record.created_at,
        updatedAt=record.updated_at,
    )


def serialize_fact(record: VaultFact) -> VaultFactRecord:
    return VaultFactRecord(
        id=record.id,
        kind=record.kind,
        statement=record.statement,
        evidence=record.evidence,
        sourceType=record.source_type,
        reviewState=record.review_state,
        memoryTier=record.memory_tier,
        validationStatus=record.validation_status,
        contaminationRisk=record.contamination_risk,
        quarantineReason=record.quarantine_reason,
        feasibilityChecks=record.feasibility_checks,
        draftEligible=record.draft_eligible,
        details=record.details,
        createdAt=record.created_at,
        updatedAt=record.updated_at,
    )


def serialize_bullet(record: VaultBulletCandidate) -> VaultBulletCandidateRecord:
    return VaultBulletCandidateRecord(
        id=record.id,
        text=record.text,
        storyAngle=record.story_angle,
        sourceType=record.source_type,
        reviewState=record.review_state,
        memoryTier=record.memory_tier,
        validationStatus=record.validation_status,
        contaminationRisk=record.contamination_risk,
        quarantineReason=record.quarantine_reason,
        feasibilityChecks=record.feasibility_checks,
        draftEligible=record.draft_eligible,
        supportingFactIds=[fact.id for fact in record.supporting_facts],
        details=record.details,
        createdAt=record.created_at,
        updatedAt=record.updated_at,
    )


def build_fact(
    *,
    role: VaultRole,
    project_story: VaultProjectStory | None,
    payload: VaultFactInput,
) -> VaultFact:
    return VaultFact(
        role=role,
        project_story=project_story,
        kind=payload.kind,
        statement=payload.statement,
        evidence=payload.evidence,
        source_type=payload.source_type,
        review_state=payload.review_state,
        memory_tier=payload.memory_tier,
        validation_status=payload.validation_status,
        contamination_risk=payload.contamination_risk,
        quarantine_reason=payload.quarantine_reason,
        feasibility_checks=payload.feasibility_checks,
        draft_eligible=payload.draft_eligible,
        details=payload.details,
    )


def build_bullet(
    *,
    role: VaultRole,
    project_story: VaultProjectStory | None,
    payload: VaultBulletCandidateInput,
    fact_lookup: dict[str, VaultFact],
) -> VaultBulletCandidate:
    bullet = VaultBulletCandidate(
        role=role,
        project_story=project_story,
        text=payload.text,
        story_angle=payload.story_angle,
        source_type=payload.source_type,
        review_state=payload.review_state,
        memory_tier=payload.memory_tier,
        validation_status=payload.validation_status,
        contamination_risk=payload.contamination_risk,
        quarantine_reason=payload.quarantine_reason,
        feasibility_checks=payload.feasibility_checks,
        draft_eligible=payload.draft_eligible,
        details=payload.details,
    )
    bullet.supporting_facts = [
        fact_lookup[client_key]
        for client_key in payload.supporting_fact_client_keys
        if client_key in fact_lookup
    ]
    return bullet
