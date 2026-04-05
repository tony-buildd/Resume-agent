from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StageKey(str, Enum):
    BOOTSTRAP = "bootstrap"
    VAULT_SEED_IMPORT = "vault_seed_import"
    VAULT_ROLE_INTERVIEW = "vault_role_interview"
    VAULT_STORY_CHECKPOINT = "vault_story_checkpoint"
    JD_INTAKE = "jd_intake"
    JD_ANALYSIS_REVIEW = "jd_analysis_review"
    CAREER_INTAKE = "career_intake"
    BLUEPRINT_REVIEW = "blueprint_review"
    DRAFT_REVIEW = "draft_review"
    COMPLETE = "complete"


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    INTERRUPTED = "interrupted"
    COMPLETE = "complete"


class InterruptReason(str, Enum):
    AWAITING_VAULT_SEED = "awaiting_vault_seed"
    AWAITING_VAULT_ROLE_DETAILS = "awaiting_vault_role_details"
    AWAITING_VAULT_CHECKPOINT_APPROVAL = "awaiting_vault_checkpoint_approval"
    AWAITING_JOB_DESCRIPTION = "awaiting_job_description"
    AWAITING_JD_ANALYSIS_APPROVAL = "awaiting_jd_analysis_approval"
    AWAITING_EXPERIENCE_DETAILS = "awaiting_experience_details"
    AWAITING_BLUEPRINT_APPROVAL = "awaiting_blueprint_approval"
    NONE = "none"


class RuntimeStage(BaseModel):
    key: StageKey
    label: str
    status: StageStatus
    summary: str
    interrupt_reason: InterruptReason = Field(alias="interruptReason")
    can_resume: bool = Field(alias="canResume")
    updated_at: datetime = Field(alias="updatedAt")


class RuntimeArtifact(BaseModel):
    id: str
    kind: str
    status: str
    title: str
    summary: str
    payload: dict[str, object]
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class RuntimeTraceEvent(BaseModel):
    id: str
    stage: StageKey
    level: str
    message: str
    payload: dict[str, object]
    created_at: datetime = Field(alias="createdAt")


class SessionEnvelope(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    clerk_user_id: str = Field(alias="clerkUserId")
    title: str | None = None
    status: str
    stage: RuntimeStage
    stage_history: list[StageKey] = Field(alias="stageHistory")
    artifact_count: int = Field(alias="artifactCount")
    trace_event_count: int = Field(alias="traceEventCount")
    artifacts: list[RuntimeArtifact]
    trace_events: list[RuntimeTraceEvent] = Field(alias="traceEvents")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class CreateSessionRequest(BaseModel):
    title: str | None = None
    stage: StageKey = StageKey.BOOTSTRAP


class ResearchSourceRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    url: str | None = None
    note: str | None = None


class JDAnalysisRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    top_requirements: list[str] = Field(alias="topRequirements")
    primary_focus: str = Field(alias="primaryFocus")
    repeating_terms: list[str] = Field(alias="repeatingTerms")
    expected_level: str = Field(alias="expectedLevel")
    engineering_archetype: str = Field(alias="engineeringArchetype")
    business_impact: str = Field(alias="businessImpact")
    success_definition: list[str] = Field(alias="successDefinition")


class ResearchSummaryRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    company_name: str | None = Field(default=None, alias="companyName")
    role_title: str | None = Field(default=None, alias="roleTitle")
    strategic_summary: str = Field(alias="strategicSummary")
    market_signals: list[str] = Field(alias="marketSignals")
    source_notes: list[str] = Field(alias="sourceNotes")
    sources: list[ResearchSourceRecord]


class InterrogationPromptRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    prompt: str
    why_it_matters: str = Field(alias="whyItMatters")
    response_key: str = Field(alias="responseKey")
    target_requirement: str = Field(alias="targetRequirement")
    evidence_gap: str = Field(alias="evidenceGap")
    supporting_signals: list[str] = Field(alias="supportingSignals")


class AdvanceSessionRequest(BaseModel):
    answer: str | None = None
    approve_jd_analysis: bool = Field(default=False, alias="approveJdAnalysis")
    approve_blueprint: bool = Field(default=False, alias="approveBlueprint")
    approve_checkpoint: bool = Field(default=False, alias="approveCheckpoint")


class AdvanceSessionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    transition: str
    interrupted: bool
    envelope: SessionEnvelope
