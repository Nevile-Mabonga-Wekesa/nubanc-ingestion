# contracts/api/v1/system_health.py
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Literal

router = APIRouter(prefix="/v1/system", tags=["system"])

# === Schemas ===
class ConsistencyCheck(BaseModel):
    raw_vs_ledger: Literal["ok", "missing_ledger_entries"]
    raw_vs_audit: Literal["ok", "missing_audit_entries"]
    orphaned_ledger: bool
    orphaned_audit: bool
    failure_records_consistent: bool

class SystemHealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "broken"]
    environment: str
    checked_at: str
    summary: str
    checks: ConsistencyCheck

# === Helper function for veteran-level insight ===
def perform_consistency_checks(env: str) -> ConsistencyCheck:
    # In a real system, check files/DB/etc.
    # Here we mock it with safe defaults
    return ConsistencyCheck(
        raw_vs_ledger="ok",
        raw_vs_audit="ok",
        orphaned_ledger=False,
        orphaned_audit=False,
        failure_records_consistent=True
    )

# === Endpoint ===
@router.get("/health", response_model=SystemHealthResponse)
def system_health(x_tenant_id: str = Header(...), env: str = "dev"):
    """
    Returns system health and consistency checks.
    Multi-tenant aware.
    """
    try:
        checks = perform_consistency_checks(env)
        status = "healthy" if all([
            checks.raw_vs_ledger == "ok",
            checks.raw_vs_audit == "ok",
            checks.failure_records_consistent
        ]) else "degraded"

        summary = "System operating normally" if status == "healthy" else "Some inconsistencies detected"

        return SystemHealthResponse(
            status=status,
            environment=env,
            checked_at=datetime.now(timezone.utc).isoformat(),
            summary=summary,
            checks=checks
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
