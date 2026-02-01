# ingress/ingest_statements.py
from fastapi import APIRouter, Depends, Header
from contracts.api.schemas.v1.finance_statement import FinanceStatementSubmitted
from contracts.api.auth.dependencies import require_capability
from contracts.events.writer import write_raw_event
from contracts.api.config.env import require_env

routers = APIRouter()

@routers.post("/v1/ingest/statements", status_code=202)
def ingest_statements(
    body: FinanceStatementSubmitted,
    identity=Depends(require_capability("emit:raw.finance.statement")),
    x_tenant_id: str = Header(...),
    x_request_id: str = Header(...)
):
    env = require_env()

    path = write_raw_event(
        env=env,
        event_type="finance.statement.submitted.v1",
        payload=body.dict(by_alias=True),
        identity=identity.dict(),
        tenant_id=x_tenant_id
    )

    return {
        "status": "accepted",
        "event_path": path
    }
