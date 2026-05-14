# contracts/api/routes.py
"""
Organization creation route with idempotency and audit logging.

Implements NUBANC principles:
- Replayable: idempotency keys prevent duplicate processing
- Deterministic: ULID generation with state tracking
- Auditable: all operations logged with context
- Decision/Execution separation: validated before persistence
"""
import ulid
import logging
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Placeholder imports - replace with actual implementations
from contracts.api.organization_db import get_pool
from contracts.api.events import publish_event, EventPublishingError

router = APIRouter()


class CreateOrgRequest(BaseModel):
    """Request to create organization."""
    name: str = Field(..., min_length=1, max_length=255, description="Organization name")
    entity_type: str = Field(..., min_length=1, description="Entity type (corp, nonprofit, etc)")
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")

    @validator('entity_type')
    def validate_entity_type(cls, v):
        """Validate entity type is known."""
        allowed = {'corporation', 'nonprofit', 'sole_proprietor', 'partnership', 'government'}
        if v.lower() not in allowed:
            raise ValueError(f'entity_type must be one of {allowed}')
        return v.lower()

    @validator('country')
    def validate_country_code(cls, v):
        """Validate country is ISO 3166-1 alpha-2."""
        if not v.isupper() or len(v) != 2:
            raise ValueError('country must be ISO 3166-1 alpha-2 code (e.g., US, UK)')
        return v


class CreateOrgResponse(BaseModel):
    """Response from organization creation."""
    org_id: str = Field(..., description="Created organization ID")
    status: str = Field(..., description="Organization status")
    created_at: str = Field(..., description="Creation timestamp")


@router.post("/v1/organizations", response_model=CreateOrgResponse, status_code=201)
async def create_org(
    req: CreateOrgRequest,
    idempotency_key: Optional[str] = Header(default=None, description="Idempotency key for request deduplication"),
    x_tenant_id: Optional[str] = Header(default=None, description="Tenant identifier for multi-tenancy")
) -> CreateOrgResponse:
    """
    Create organization with idempotency support.
    
    Idempotency:
    - Same idempotency_key returns same result without re-processing
    - Prevents duplicate organization creation
    - Tracks via database idempotency_keys table
    
    Audit:
    - All operations logged with context
    - Event published for downstream processing
    - Timestamp recorded in UTC
    
    Args:
        req: Organization creation request
        idempotency_key: Optional key for idempotent requests
        x_tenant_id: Optional tenant identifier
        
    Returns:
        CreateOrgResponse with organization ID and status
        
    Raises:
        HTTPException: On validation or persistence failure
    """
    pool = await get_pool()
    created_at = datetime.now(timezone.utc).isoformat()
    
    try:
        async with pool.acquire() as conn:
            # === IDEMPOTENCY CHECK ===
            if idempotency_key:
                existing = await conn.fetchrow(
                    """
                    SELECT org_id, status, created_at
                    FROM idempotency_keys
                    WHERE key = $1 AND tenant_id = $2
                    """,
                    idempotency_key,
                    x_tenant_id or 'default'
                )
                if existing:
                    logger.info(
                        "Idempotent request - returning existing organization",
                        extra={
                            "org_id": existing['org_id'],
                            "idempotency_key": idempotency_key,
                            "tenant_id": x_tenant_id
                        }
                    )
                    return CreateOrgResponse(
                        org_id=existing['org_id'],
                        status=existing['status'],
                        created_at=existing['created_at']
                    )
            
            # === ORGANIZATION CREATION ===
            org_id = str(ulid.new())
            
            # Persist organization
            await conn.execute(
                """
                INSERT INTO organizations (org_id, name, entity_type, country, status, created_at)
                VALUES ($1, $2, $3, $4, 'CREATED', $5)
                """,
                org_id,
                req.name,
                req.entity_type,
                req.country,
                created_at
            )
            
            # === IDEMPOTENCY RECORD ===
            if idempotency_key:
                await conn.execute(
                    """
                    INSERT INTO idempotency_keys (key, org_id, status, tenant_id, created_at)
                    VALUES ($1, $2, 'CREATED', $3, $4)
                    """,
                    idempotency_key,
                    org_id,
                    x_tenant_id or 'default',
                    created_at
                )
            
            logger.info(
                "Organization created",
                extra={
                    "org_id": org_id,
                    "name": req.name,
                    "entity_type": req.entity_type,
                    "idempotency_key": idempotency_key,
                    "tenant_id": x_tenant_id,
                    "created_at": created_at
                }
            )
        
        # === EVENT PUBLICATION ===
        try:
            await publish_event(
                "OrganizationCreated",
                {
                    "org_id": org_id,
                    "name": req.name,
                    "entity_type": req.entity_type,
                    "country": req.country,
                    "created_at": created_at,
                    "tenant_id": x_tenant_id or 'default'
                }
            )
        except EventPublishingError as e:
            logger.error(
                "Failed to publish OrganizationCreated event",
                extra={
                    "org_id": org_id,
                    "error": str(e)
                }
            )
            # Note: Don't fail the request; event will be retried
        
        return CreateOrgResponse(
            org_id=org_id,
            status="CREATED",
            created_at=created_at
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        logger.error(
            "Failed to create organization",
            extra={"error": str(e), "error_type": type(e).__name__}
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error creating organization"
        )
