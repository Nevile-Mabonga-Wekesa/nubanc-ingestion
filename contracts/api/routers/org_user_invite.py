from fastapi import APIRouter
from contracts.api.schemas.org_user_invite import InviteUserRequest

router = APIRouter(
    prefix="/org-users",
    tags=["Organization Users"]
)

@router.post("/invite")
async def invite_user(request: InviteUserRequest):
    return {"status": "success", "email": request.email}
