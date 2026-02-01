# contracts/api/v1/org_users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from contracts.api.v1.schemas.invite import (
    InviteUserRequest,
    InviteUserResponse
)
from contracts.services.invite_service import invite_user
from contracts.db.session import get_db
from contracts.security.auth import require_org_admin  # RBAC guard
from contracts.security.context import CurrentUser

router = APIRouter(prefix="/v1/orgs")


@router.post(
    "/{org_id}/users/invite",
    response_model=InviteUserResponse,
    status_code=status.HTTP_201_CREATED
)
async def invite_org_user(
    org_id: str,
    payload: InviteUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_org_admin),
):
    if payload.role == "AUDITOR" and not current_user.is_super_admin:
        raise HTTPException(
            status_code=403,
            detail="Only super admins may invite auditors"
        )

    invite = await invite_user(
        db,
        org_id=org_id,
        email=payload.email.lower(),
        role=payload.role,
        invited_by=current_user.user_id,
    )

    return InviteUserResponse(
        invite_id=invite.id,
        status=invite.status,
        expires_at=invite.expires_at,
    )
