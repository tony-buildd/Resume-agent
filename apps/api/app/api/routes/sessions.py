from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import AppUser, SessionRecord
from app.db.session import get_db_session
from app.orchestration.contracts import (
    AdvanceSessionRequest,
    AdvanceSessionResponse,
    CreateSessionRequest,
    SessionEnvelope,
)
from app.orchestration.runtime import advance_session, build_session_envelope

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class AuthContext(BaseModel):
    clerk_user_id: str
    email_address: str | None = None


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

    elif auth.email_address and user.email_address != auth.email_address:
        user.email_address = auth.email_address
        db.flush()

    return user


def get_user_owned_session(
    db: Session,
    *,
    session_id: str,
    clerk_user_id: str,
) -> SessionRecord:
    record = db.scalar(
        select(SessionRecord)
        .join(AppUser)
        .options(
            selectinload(SessionRecord.user),
            selectinload(SessionRecord.artifacts),
            selectinload(SessionRecord.trace_events),
        )
        .where(
            SessionRecord.id == session_id,
            AppUser.clerk_user_id == clerk_user_id,
        )
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found for current user.",
        )

    return record


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
        stage=payload.stage.value,
    )
    record.user = user
    db.add(record)
    db.flush()

    advance_session(db, record)

    db.commit()
    db.refresh(record)
    return build_session_envelope(record, auth.clerk_user_id)


@router.get("/{session_id}", response_model=SessionEnvelope)
def get_session(
    session_id: str,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> SessionEnvelope:
    record = get_user_owned_session(
        db,
        session_id=session_id,
        clerk_user_id=auth.clerk_user_id,
    )
    return build_session_envelope(record, auth.clerk_user_id)


@router.post("/{session_id}/advance", response_model=AdvanceSessionResponse)
def advance_existing_session(
    session_id: str,
    payload: AdvanceSessionRequest,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> AdvanceSessionResponse:
    record = get_user_owned_session(
        db,
        session_id=session_id,
        clerk_user_id=auth.clerk_user_id,
    )
    response = advance_session(
        db,
        record,
        answer=payload.answer,
        approve_jd_analysis=payload.approve_jd_analysis,
        approve_blueprint=payload.approve_blueprint,
        accept_draft_review=payload.accept_draft_review,
        request_revision=payload.request_revision,
    )
    db.commit()
    db.refresh(record)
    return AdvanceSessionResponse(
        transition=response.transition,
        interrupted=response.interrupted,
        envelope=build_session_envelope(record, auth.clerk_user_id),
    )
