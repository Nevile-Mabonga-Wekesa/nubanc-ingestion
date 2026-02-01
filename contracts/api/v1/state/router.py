from fastapi import APIRouter, Header, HTTPException
from typing import Optional
import os

from .models import StateResponse
from .service import compute_entity_state


router = APIRouter(prefix="/v1/state", tags=["state"])


@router.get("/{entity_type}/{entity_id}", response_model=StateResponse)
def get_state(
    entity_type: str,
    entity_id: str,
    x_tenant_id: str = Header(..., alias="X-Tenant-Id"),
    x_as_of_timestamp: Optional[str] = Header(None, alias="X-As-Of-Timestamp"),
):
    env = os.getenv("NUBANC_ENV", "dev")

    if not entity_type or not entity_id:
        raise HTTPException(status_code=400, detail="Invalid entity reference")

    return compute_entity_state(
        env=env,
        tenant_id=x_tenant_id,
        entity_type=entity_type,
        entity_id=entity_id,
        as_of=x_as_of_timestamp,
    )
