from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.routes.sessions import AuthContext, get_auth_context, get_or_create_user
from app.db.models import VaultRole
from app.db.session import get_db_session
from app.vault.contracts import CreateVaultRoleRequest, VaultRoleRecord
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
