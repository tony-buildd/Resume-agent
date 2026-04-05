from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.sessions import AuthContext, get_auth_context, get_or_create_user
from app.db.models import VaultRole
from app.db.session import get_db_session
from app.vault.contracts import (
    CreateVaultRoleRequest,
    GuidedRoleCaptureRequest,
    SeedImportRequest,
    VaultIngestionResponse,
    VaultRoleRecord,
)
from app.vault.ingestion import (
    build_guided_capture_request,
    build_ingestion_response,
    build_seed_import_request,
)
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


@router.post("/interviews/roles", response_model=VaultIngestionResponse, status_code=201)
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
