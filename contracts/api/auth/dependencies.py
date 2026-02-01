# auth/dependencies.py
from fastapi import Depends, HTTPException, status
from auth.identity import resolve_identity
from pydantic import BaseModel
from typing import List

class Identity(BaseModel):
    user_id: str
    capabilities: List[str]


# Stub identity for local dev
def get_identity() -> Identity:
    # Always return a valid identity in dev
    return Identity(
        user_id="local-dev",
        capabilities=["INGEST_STATEMENTS"]
    )

def require_capability(capability: str):
    def _checker(identity: Identity = Depends(get_identity)):
        if capability not in identity.capabilities:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient capability",
            )
        return True

    return _checker
