from fastapi import Header, HTTPException
from auth.identity import IdentityContext
from api.config.environment import get_env

def authenticate(
    authorization: str = Header(...)
) -> IdentityContext:
    """
    Placeholder authentication adapter.
    Replace token verification later (JWT, Cognito, etc).
    """

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.replace("Bearer ", "")

    # TEMP: deterministic identity stub
    # This will later be replaced by real token verification
    return IdentityContext(
        identity_id="service_api_client",
        tenant_id="tenant_demo",
        environment=get_env(),
        capabilities=[
            "emit:raw.credit.application",
            "request:credit.assessment",
            "read:ledger.credit"
        ],
        identity_type="service"
    )
