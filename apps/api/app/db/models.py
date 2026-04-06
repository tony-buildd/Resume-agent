from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    JSON,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


def generate_id() -> str:
    return str(uuid4())


class SessionStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    INTERRUPTED = "interrupted"
    COMPLETE = "complete"


class ArtifactStatus(str, Enum):
    CANDIDATE = "candidate"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANONICAL = "canonical"


class EventLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class VaultSourceType(str, Enum):
    SEED_MATERIAL = "seed_material"
    INTERVIEW_ANSWER = "interview_answer"
    AGENT_INFERENCE = "agent_inference"


class VaultReviewState(str, Enum):
    USER_STATED = "user_stated"
    INFERRED = "inferred"
    APPROVED = "approved"
    REJECTED = "rejected"


class VaultMemoryTier(str, Enum):
    CANONICAL = "canonical"
    PROGRESS = "progress"
    FEASIBILITY = "feasibility"
    QUARANTINE = "quarantine"


class VaultValidationStatus(str, Enum):
    UNCHECKED = "unchecked"
    NEEDS_REVIEW = "needs_review"
    VALIDATED = "validated"
    FAILED = "failed"


class VaultContaminationRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class VaultQuarantineReason(str, Enum):
    NONE = "none"
    LOW_CONFIDENCE = "low_confidence"
    CONTRADICTION = "contradiction"
    UNSUPPORTED_METRIC = "unsupported_metric"
    CROSS_ROLE_LEAKAGE = "cross_role_leakage"
    USER_FLAGGED = "user_flagged"


bullet_candidate_fact_links = Table(
    "bullet_candidate_fact_links",
    Base.metadata,
    Column(
        "bullet_candidate_id",
        String(36),
        ForeignKey("vault_bullet_candidates.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "fact_id",
        String(36),
        ForeignKey("vault_facts.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class AppUser(TimestampMixin, Base):
    __tablename__ = "app_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    clerk_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email_address: Mapped[str | None] = mapped_column(String(320), nullable=True)

    sessions: Mapped[list["SessionRecord"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    vault_companies: Mapped[list["VaultCompany"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class SessionRecord(TimestampMixin, Base):
    __tablename__ = "session_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage: Mapped[str] = mapped_column(String(120), nullable=False, default="bootstrap")
    status: Mapped[SessionStatus] = mapped_column(
        SqlEnum(SessionStatus),
        nullable=False,
        default=SessionStatus.DRAFT,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state_snapshot: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )

    user: Mapped[AppUser] = relationship(back_populates="sessions")
    artifacts: Mapped[list["ArtifactRecord"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )
    trace_events: Mapped[list["TraceEventRecord"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class ArtifactRecord(TimestampMixin, Base):
    __tablename__ = "artifact_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("session_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[ArtifactStatus] = mapped_column(
        SqlEnum(ArtifactStatus),
        nullable=False,
        default=ArtifactStatus.CANDIDATE,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    session: Mapped[SessionRecord] = relationship(back_populates="artifacts")


class TraceEventRecord(TimestampMixin, Base):
    __tablename__ = "trace_event_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("session_records.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage: Mapped[str] = mapped_column(String(120), nullable=False)
    level: Mapped[EventLevel] = mapped_column(
        SqlEnum(EventLevel),
        nullable=False,
        default=EventLevel.INFO,
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    session: Mapped[SessionRecord] = relationship(back_populates="trace_events")


class VaultCompany(TimestampMixin, Base):
    __tablename__ = "vault_companies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("app_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped[AppUser] = relationship(back_populates="vault_companies")
    roles: Mapped[list["VaultRole"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )


class VaultRole(TimestampMixin, Base):
    __tablename__ = "vault_roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    company_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("vault_companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    company: Mapped[VaultCompany] = relationship(back_populates="roles")
    project_stories: Mapped[list["VaultProjectStory"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )
    facts: Mapped[list["VaultFact"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )
    bullet_candidates: Mapped[list["VaultBulletCandidate"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )


class VaultProjectStory(TimestampMixin, Base):
    __tablename__ = "vault_project_stories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("vault_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[VaultSourceType] = mapped_column(
        SqlEnum(VaultSourceType),
        nullable=False,
        default=VaultSourceType.INTERVIEW_ANSWER,
    )
    review_state: Mapped[VaultReviewState] = mapped_column(
        SqlEnum(VaultReviewState),
        nullable=False,
        default=VaultReviewState.USER_STATED,
    )
    memory_tier: Mapped[VaultMemoryTier] = mapped_column(
        SqlEnum(VaultMemoryTier),
        nullable=False,
        default=VaultMemoryTier.CANONICAL,
    )
    validation_status: Mapped[VaultValidationStatus] = mapped_column(
        SqlEnum(VaultValidationStatus),
        nullable=False,
        default=VaultValidationStatus.UNCHECKED,
    )
    contamination_risk: Mapped[VaultContaminationRisk] = mapped_column(
        SqlEnum(VaultContaminationRisk),
        nullable=False,
        default=VaultContaminationRisk.LOW,
    )
    quarantine_reason: Mapped[VaultQuarantineReason] = mapped_column(
        SqlEnum(VaultQuarantineReason),
        nullable=False,
        default=VaultQuarantineReason.NONE,
    )
    feasibility_checks: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    draft_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    role: Mapped[VaultRole] = relationship(back_populates="project_stories")
    facts: Mapped[list["VaultFact"]] = relationship(
        back_populates="project_story",
        cascade="all, delete-orphan",
    )
    bullet_candidates: Mapped[list["VaultBulletCandidate"]] = relationship(
        back_populates="project_story",
        cascade="all, delete-orphan",
    )


class VaultFact(TimestampMixin, Base):
    __tablename__ = "vault_facts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("vault_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_story_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vault_project_stories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    kind: Mapped[str] = mapped_column(String(120), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[VaultSourceType] = mapped_column(
        SqlEnum(VaultSourceType),
        nullable=False,
        default=VaultSourceType.INTERVIEW_ANSWER,
    )
    review_state: Mapped[VaultReviewState] = mapped_column(
        SqlEnum(VaultReviewState),
        nullable=False,
        default=VaultReviewState.USER_STATED,
    )
    memory_tier: Mapped[VaultMemoryTier] = mapped_column(
        SqlEnum(VaultMemoryTier),
        nullable=False,
        default=VaultMemoryTier.CANONICAL,
    )
    validation_status: Mapped[VaultValidationStatus] = mapped_column(
        SqlEnum(VaultValidationStatus),
        nullable=False,
        default=VaultValidationStatus.UNCHECKED,
    )
    contamination_risk: Mapped[VaultContaminationRisk] = mapped_column(
        SqlEnum(VaultContaminationRisk),
        nullable=False,
        default=VaultContaminationRisk.LOW,
    )
    quarantine_reason: Mapped[VaultQuarantineReason] = mapped_column(
        SqlEnum(VaultQuarantineReason),
        nullable=False,
        default=VaultQuarantineReason.NONE,
    )
    feasibility_checks: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    draft_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    role: Mapped[VaultRole] = relationship(back_populates="facts")
    project_story: Mapped[VaultProjectStory | None] = relationship(
        back_populates="facts"
    )
    bullet_candidates: Mapped[list["VaultBulletCandidate"]] = relationship(
        secondary=bullet_candidate_fact_links,
        back_populates="supporting_facts",
    )


class VaultBulletCandidate(TimestampMixin, Base):
    __tablename__ = "vault_bullet_candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("vault_roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    project_story_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("vault_project_stories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    story_angle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_type: Mapped[VaultSourceType] = mapped_column(
        SqlEnum(VaultSourceType),
        nullable=False,
        default=VaultSourceType.AGENT_INFERENCE,
    )
    review_state: Mapped[VaultReviewState] = mapped_column(
        SqlEnum(VaultReviewState),
        nullable=False,
        default=VaultReviewState.INFERRED,
    )
    memory_tier: Mapped[VaultMemoryTier] = mapped_column(
        SqlEnum(VaultMemoryTier),
        nullable=False,
        default=VaultMemoryTier.CANONICAL,
    )
    validation_status: Mapped[VaultValidationStatus] = mapped_column(
        SqlEnum(VaultValidationStatus),
        nullable=False,
        default=VaultValidationStatus.UNCHECKED,
    )
    contamination_risk: Mapped[VaultContaminationRisk] = mapped_column(
        SqlEnum(VaultContaminationRisk),
        nullable=False,
        default=VaultContaminationRisk.LOW,
    )
    quarantine_reason: Mapped[VaultQuarantineReason] = mapped_column(
        SqlEnum(VaultQuarantineReason),
        nullable=False,
        default=VaultQuarantineReason.NONE,
    )
    feasibility_checks: Mapped[dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    draft_eligible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    role: Mapped[VaultRole] = relationship(back_populates="bullet_candidates")
    project_story: Mapped[VaultProjectStory | None] = relationship(
        back_populates="bullet_candidates"
    )
    supporting_facts: Mapped[list[VaultFact]] = relationship(
        secondary=bullet_candidate_fact_links,
        back_populates="bullet_candidates",
    )
