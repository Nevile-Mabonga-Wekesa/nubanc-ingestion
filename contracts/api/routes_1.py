# routes_route.py
import ulid
from fastapi import APIRouter, Header, HTTPException
from contracts.api.organization_db import get_pool
from contracts.api.models import CreateOrgRequest, CreateOrgResponse
from contracts.api.events import publish_event

router = APIRouter()

def generate_event_id() -> str:
    return str(ulid.new())

event_id = generate_event_id()
print(event_id)

@router.post("/v1/organizations", response_model=CreateOrgResponse, status_code=201)
async def create_org(
    req: CreateOrgRequest,
    idempotency_key: str | None = Header(default=None)
):
    pool = await get_pool()

    async with pool.acquire() as conn:
        if idempotency_key:
            existing = await conn.fetchrow(
                """
                SELECT org_id, status
                FROM idempotency_keys
                WHERE key = $1
                """,
                idempotency_key
            )
            if existing:
                return dict(existing)

        org_id = str(ulid.new())

        await conn.execute(
            """
            INSERT INTO organizations (org_id, name, entity_type, country, status)
            VALUES ($1, $2, $3, $4, 'CREATED')
            """,
            org_id, req.name, req.entity_type, req.country
        )

        if idempotency_key:
            await conn.execute(
                """
                INSERT INTO idempotency_keys (key, org_id, status)
                VALUES ($1, $2, 'CREATED')
                """,
                idempotency_key, org_id
            )

    await publish_event(
        "OrganizationCreated",
        {"org_id": org_id, "entity_type": req.entity_type}
    )

    return {"org_id": org_id, "status": "CREATED"}
