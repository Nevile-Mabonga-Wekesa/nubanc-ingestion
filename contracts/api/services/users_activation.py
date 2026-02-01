from contracts.api.db.repositories.users import UserRepository
from contracts.api.audits.events import emit_user_activated
from fastapi import HTTPException
from contracts.api.security.token import decode_activation_token

class UserActivationService:

    @staticmethod
    async def activate(*, conn, token: str):
        payload = decode_activation_token(token)

        user_id = payload["user_id"]
        org_id = payload["org_id"]

        user = await UserRepository.get_by_id(conn, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user["status"] == "ACTIVE":
            return  # idempotent success

        if user["status"] != "PENDING_ACTIVATION":
            raise HTTPException(
                status_code=409,
                detail=f"Cannot activate user in state {user['status']}"
            )

        if not user["org_active"]:
            raise HTTPException(
                status_code=403,
                detail="Organization is inactive"
            )

        await UserRepository.activate_user(conn, user_id)

        await emit_user_activated(
            conn,
            user_id=user_id,
            org_id=org_id,
            actor="SELF"
        )
    def __init__(self, db):
        self.db = db

