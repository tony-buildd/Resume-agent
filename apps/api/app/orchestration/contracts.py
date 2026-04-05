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


class AdvanceSessionRequest(BaseModel):
    answer: str | None = None
    approve_blueprint: bool = Field(default=False, alias="approveBlueprint")
    approve_checkpoint: bool = Field(default=False, alias="approveCheckpoint")


class AdvanceSessionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    transition: str
    interrupted: bool
    envelope: SessionEnvelope
