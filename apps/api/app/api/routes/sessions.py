from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AppUser, SessionRecord
from app.db.session import get_db_session

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class AuthContext(BaseModel):
    clerk_user_id: str
    email_address: str | None = None


class CreateSessionRequest(BaseModel):
    title: str | None = None
    stage: str = "bootstrap"


class SessionEnvelope(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    user_id: str = Field(alias="userId")
    clerk_user_id: str = Field(alias="clerkUserId")
    title: str | None = None
    stage: str
    status: str
    artifact_count: int = Field(alias="artifactCount")
    trace_event_count: int = Field(alias="traceEventCount")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


DbSession = Annotated[Session, Depends(get_db_session)]


def get_auth_context(
    clerk_user_id: Annotated[str | None, Header(alias="X-Clerk-User-Id")] = None,
    email_address: Annotated[str | None, Header(alias="X-Clerk-User-Email")] = None,
) -> AuthContext:
    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Clerk-User-Id header.",
        )

    return AuthContext(
        clerk_user_id=clerk_user_id,
        email_address=email_address,
    )


def get_or_create_user(db: Session, auth: AuthContext) -> AppUser:
    user = db.scalar(
        select(AppUser).where(AppUser.clerk_user_id == auth.clerk_user_id)
    )

    if user is None:
        user = AppUser(
            clerk_user_id=auth.clerk_user_id,
            email_address=auth.email_address,
        )
        db.add(user)
        db.flush()

    return user


def to_session_envelope(record: SessionRecord, auth: AuthContext) -> SessionEnvelope:
    return SessionEnvelope(
        id=record.id,
        userId=record.user_id,
        clerkUserId=auth.clerk_user_id,
        title=record.title,
        stage=record.stage,
        status=record.status.value,
        artifactCount=len(record.artifacts),
        traceEventCount=len(record.trace_events),
        createdAt=record.created_at,
        updatedAt=record.updated_at,
    )


@router.post("", response_model=SessionEnvelope, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: CreateSessionRequest,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> SessionEnvelope:
    user = get_or_create_user(db, auth)
    record = SessionRecord(
        user_id=user.id,
        title=payload.title,
        stage=payload.stage,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return to_session_envelope(record, auth)


@router.get("/{session_id}", response_model=SessionEnvelope)
def get_session(
    session_id: str,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> SessionEnvelope:
    record = db.scalar(
        select(SessionRecord)
        .join(AppUser)
        .where(
            SessionRecord.id == session_id,
            AppUser.clerk_user_id == auth.clerk_user_id,
        )
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found for current user.",
        )

    return to_session_envelope(record, auth)
