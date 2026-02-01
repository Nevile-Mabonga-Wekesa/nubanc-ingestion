# contracts/services/invite_service.py
import hashlib
import secrets
from datetime import datetime, timedelta
from ulid import ULID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from contracts.db.models.org_user_invite import OrgUserInvite, InviteStatus


INVITE_TTL_HOURS = 24


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def invite_user(
    db: AsyncSession,
    *,
    org_id: str,
    email: str,
    role: str,
    invited_by: str
) -> OrgUserInvite:
    # Idempotency: check existing invite
    q = select(OrgUserInvite).where(
        OrgUserInvite.org_id == org_id,
        OrgUserInvite.email == email,
        OrgUserInvite.status == InviteStatus.INVITED
    )
    existing = (await db.execute(q)).scalar_one_or_none()
    if existing:
        return existing

    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_token(raw_token)

    invite = OrgUserInvite(
        id=str(ULID()),
        org_id=org_id,
        email=email,
        role=role,
        status=InviteStatus.INVITED,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=INVITE_TTL_HOURS),
        invited_by=invited_by,
    )

    db.add(invite)
    await db.commit()
    await db.refresh(invite)

    # Email dispatch would happen here (async task)
    return invite
