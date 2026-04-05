from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, JSON, String, Text, func
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


class AppUser(TimestampMixin, Base):
    __tablename__ = "app_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_id)
    clerk_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email_address: Mapped[str | None] = mapped_column(String(320), nullable=True)

    sessions: Mapped[list["SessionRecord"]] = relationship(
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
    state_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

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
