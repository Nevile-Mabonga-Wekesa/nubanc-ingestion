from fastapi import APIRouter, Depends
from contracts.api.schemas.users import UserActivateRequest
from contracts.api.services.users_activation import UserActivationService
from contracts.api.deps.db import get_db_conn
router = APIRouter(prefix="/v1/users")

@router.post("/activate", status_code=200)
async def activate_user(
    payload: UserActivateRequest,
    conn = Depends(get_db_conn)
):
    await UserActivationService.activate(
        conn=conn,
        token=payload.activation_token
    )
    return {"status": "activated"}
