from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.sessions import (
    AuthContext,
    get_auth_context,
    get_or_create_user,
    get_user_owned_session,
)
from app.db.models import SessionRecord, VaultRole
from app.db.session import get_db_session
from app.orchestration.contracts import (
    AdvanceSessionRequest,
    AdvanceSessionResponse,
    SessionEnvelope,
    StageKey,
)
from app.orchestration.runtime import advance_session, build_session_envelope
from app.vault.contracts import (
    CreateVaultInterviewSessionRequest,
    CreateVaultRoleRequest,
    GuidedRoleCaptureRequest,
    SeedImportRequest,
    VaultIngestionResponse,
    VaultRetrievalRequest,
    VaultRetrievalResponse,
    VaultRoleRecord,
)
from app.vault.ingestion import (
    build_guided_capture_request,
    build_ingestion_response,
    build_seed_import_request,
)
from app.vault.retrieval import retrieve_vault_context
from app.vault.service import (
    base_vault_role_query,
    create_vault_role_tree,
    list_vault_roles,
    serialize_vault_role,
)

router = APIRouter(prefix="/api/vault", tags=["vault"])

DbSession = Annotated[Session, Depends(get_db_session)]


@router.post("/roles", response_model=VaultRoleRecord, status_code=201)
def create_vault_role(
    payload: CreateVaultRoleRequest,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> VaultRoleRecord:
    user = get_or_create_user(db, auth)
    role = create_vault_role_tree(
        db,
        user=user,
        payload=payload,
    )
    db.commit()

    record = db.scalar(base_vault_role_query().where(VaultRole.id == role.id))
    assert record is not None
    return serialize_vault_role(record)


@router.get("/roles", response_model=list[VaultRoleRecord])
def get_vault_roles(
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> list[VaultRoleRecord]:
    user = get_or_create_user(db, auth)
    records = list_vault_roles(db, user=user)
    return [serialize_vault_role(record) for record in records]


@router.post("/retrieval", response_model=VaultRetrievalResponse)
def retrieve_vault(
    payload: VaultRetrievalRequest,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> VaultRetrievalResponse:
    user = get_or_create_user(db, auth)
    return retrieve_vault_context(
        db,
        user=user,
        query=payload.query,
        limit=payload.limit,
        story_limit=payload.story_limit,
        evidence_limit=payload.evidence_limit,
        include_semantic=payload.include_semantic,
    )


@router.post("/imports/seed", response_model=VaultIngestionResponse, status_code=201)
def import_seed_material(
    payload: SeedImportRequest,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> VaultIngestionResponse:
    user = get_or_create_user(db, auth)
    request_payload = build_seed_import_request(payload)
    role = create_vault_role_tree(db, user=user, payload=request_payload)
    db.commit()

    record = db.scalar(base_vault_role_query().where(VaultRole.id == role.id))
    assert record is not None
    return build_ingestion_response("seed_import", serialize_vault_role(record))


@router.post(
    "/interviews/roles", response_model=VaultIngestionResponse, status_code=201
)
def capture_guided_role(
    payload: GuidedRoleCaptureRequest,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> VaultIngestionResponse:
    user = get_or_create_user(db, auth)
    request_payload = build_guided_capture_request(payload)
    role = create_vault_role_tree(db, user=user, payload=request_payload)
    db.commit()

    record = db.scalar(base_vault_role_query().where(VaultRole.id == role.id))
    assert record is not None
    return build_ingestion_response("guided_capture", serialize_vault_role(record))


@router.post("/interview-sessions", response_model=SessionEnvelope, status_code=201)
def create_vault_interview_session(
    payload: CreateVaultInterviewSessionRequest,
    auth: Annotated[AuthContext, Depends(get_auth_context)],
    db: DbSession,
) -> SessionEnvelope:
    user = get_or_create_user(db, auth)
    record = SessionRecord(
        user_id=user.id,
        title=f"Vault interview: {payload.title}",
        stage=StageKey.BOOTSTRAP.value,
        state_snapshot={
            "runtime": {
                "flow": "vault_ingestion",
                "vault_company_name": payload.company_name,
                "vault_role_title": payload.title,
                "vault_story_name": payload.story_name,
                "vault_role_summary": payload.role_summary,
                "vault_stack_summary": payload.stack_summary,
                "vault_impact_summary": payload.impact_summary,
            }
        },
    )
    record.user = user
    db.add(record)
    db.flush()

    advance_session(db, record)
    db.commit()
    db.refresh(record)
    return build_session_envelope(record, auth.clerk_user_id)


@router.post(
    "/interview-sessions/{session_id}/advance",
    response_model=AdvanceSessionResponse,
)
def advance_vault_interview_session(
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
        approve_checkpoint=payload.approve_checkpoint,
    )
    db.commit()
    db.refresh(record)
    return AdvanceSessionResponse(
        transition=response.transition,
        interrupted=response.interrupted,
        envelope=build_session_envelope(record, auth.clerk_user_id),
    )
