from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import VaultReviewState, VaultSourceType


class VaultFactInput(BaseModel):
    client_key: str = Field(alias="clientKey")
    kind: str
    statement: str
    evidence: str | None = None
    source_type: VaultSourceType = Field(alias="sourceType")
    review_state: VaultReviewState = Field(alias="reviewState")
    draft_eligible: bool = Field(alias="draftEligible")
    details: dict[str, object] = Field(default_factory=dict)


class VaultBulletCandidateInput(BaseModel):
    text: str
    story_angle: str | None = Field(default=None, alias="storyAngle")
    source_type: VaultSourceType = Field(alias="sourceType")
    review_state: VaultReviewState = Field(alias="reviewState")
    draft_eligible: bool = Field(alias="draftEligible")
    supporting_fact_client_keys: list[str] = Field(
        default_factory=list,
        alias="supportingFactClientKeys",
    )
    details: dict[str, object] = Field(default_factory=dict)


class VaultProjectStoryInput(BaseModel):
    client_key: str = Field(alias="clientKey")
    name: str
    summary: str | None = None
    stack_summary: str | None = Field(default=None, alias="stackSummary")
    impact_summary: str | None = Field(default=None, alias="impactSummary")
    source_type: VaultSourceType = Field(alias="sourceType")
    review_state: VaultReviewState = Field(alias="reviewState")
    draft_eligible: bool = Field(alias="draftEligible")
    details: dict[str, object] = Field(default_factory=dict)
    facts: list[VaultFactInput] = Field(default_factory=list)
    bullet_candidates: list[VaultBulletCandidateInput] = Field(
        default_factory=list,
        alias="bulletCandidates",
    )


class CreateVaultRoleRequest(BaseModel):
    company_name: str = Field(alias="companyName")
    company_domain: str | None = Field(default=None, alias="companyDomain")
    company_summary: str | None = Field(default=None, alias="companySummary")
    title: str
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")
    location: str | None = None
    employment_type: str | None = Field(default=None, alias="employmentType")
    summary: str | None = None
    details: dict[str, object] = Field(default_factory=dict)
    role_facts: list[VaultFactInput] = Field(default_factory=list, alias="roleFacts")
    role_bullet_candidates: list[VaultBulletCandidateInput] = Field(
        default_factory=list,
        alias="roleBulletCandidates",
    )
    project_stories: list[VaultProjectStoryInput] = Field(
        default_factory=list,
        alias="projectStories",
    )


class VaultFactRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    kind: str
    statement: str
    evidence: str | None = None
    source_type: VaultSourceType = Field(alias="sourceType")
    review_state: VaultReviewState = Field(alias="reviewState")
    draft_eligible: bool = Field(alias="draftEligible")
    details: dict[str, object]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class VaultBulletCandidateRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    text: str
    story_angle: str | None = Field(default=None, alias="storyAngle")
    source_type: VaultSourceType = Field(alias="sourceType")
    review_state: VaultReviewState = Field(alias="reviewState")
    draft_eligible: bool = Field(alias="draftEligible")
    supporting_fact_ids: list[str] = Field(alias="supportingFactIds")
    details: dict[str, object]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class VaultProjectStoryRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    summary: str | None = None
    stack_summary: str | None = Field(default=None, alias="stackSummary")
    impact_summary: str | None = Field(default=None, alias="impactSummary")
    source_type: VaultSourceType = Field(alias="sourceType")
    review_state: VaultReviewState = Field(alias="reviewState")
    draft_eligible: bool = Field(alias="draftEligible")
    details: dict[str, object]
    facts: list[VaultFactRecord]
    bullet_candidates: list[VaultBulletCandidateRecord] = Field(
        alias="bulletCandidates"
    )
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class VaultCompanyRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    domain: str | None = None
    summary: str | None = None
    details: dict[str, object]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class VaultRoleRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")
    location: str | None = None
    employment_type: str | None = Field(default=None, alias="employmentType")
    summary: str | None = None
    details: dict[str, object]
    company: VaultCompanyRecord
    role_facts: list[VaultFactRecord] = Field(alias="roleFacts")
    role_bullet_candidates: list[VaultBulletCandidateRecord] = Field(
        alias="roleBulletCandidates"
    )
    project_stories: list[VaultProjectStoryRecord] = Field(alias="projectStories")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class SeedImportRequest(BaseModel):
    company_name: str = Field(alias="companyName")
    title: str
    seed_text: str = Field(alias="seedText")
    story_name: str | None = Field(default=None, alias="storyName")
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")
    location: str | None = None


class GuidedRoleCaptureRequest(BaseModel):
    company_name: str = Field(alias="companyName")
    title: str
    role_summary: str | None = Field(default=None, alias="roleSummary")
    story_name: str = Field(alias="storyName")
    raw_details: str = Field(alias="rawDetails")
    stack_summary: str | None = Field(default=None, alias="stackSummary")
    impact_summary: str | None = Field(default=None, alias="impactSummary")
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")
    location: str | None = None


class StoryCheckpointRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    role_title: str = Field(alias="roleTitle")
    story_name: str = Field(alias="storyName")
    total_facts: int = Field(alias="totalFacts")
    draft_eligible_facts: int = Field(alias="draftEligibleFacts")
    pending_review_facts: int = Field(alias="pendingReviewFacts")
    suggested_next_question: str = Field(alias="suggestedNextQuestion")
    missing_signals: list[str] = Field(alias="missingSignals")


class VaultIngestionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    mode: str
    role: VaultRoleRecord
    checkpoint: StoryCheckpointRecord


class CreateVaultInterviewSessionRequest(BaseModel):
    company_name: str = Field(alias="companyName")
    title: str
    story_name: str = Field(alias="storyName")
    role_summary: str | None = Field(default=None, alias="roleSummary")
    stack_summary: str | None = Field(default=None, alias="stackSummary")
    impact_summary: str | None = Field(default=None, alias="impactSummary")


class VaultRetrievalRequest(BaseModel):
    query: str | None = None
    limit: int = Field(default=5, ge=1, le=20)
    include_semantic: bool = Field(default=True, alias="includeSemantic")


class VaultSemanticMatchRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    document: str
    metadata: dict[str, object]
    distance: float | None = None


class VaultRetrievalResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    query: str | None = None
    draft_safe_roles: list[VaultRoleRecord] = Field(alias="draftSafeRoles")
    questioning_safe_roles: list[VaultRoleRecord] = Field(alias="questioningSafeRoles")
    semantic_matches: list[VaultSemanticMatchRecord] = Field(
        default_factory=list,
        alias="semanticMatches",
    )
