from typing import Literal, Dict
from pydantic import BaseModel


class ConsistencyChecks(BaseModel):
    raw_vs_ledger: Literal["ok", "missing_ledger_entries"]
    raw_vs_audit: Literal["ok", "missing_audit_entries"]
    orphaned_ledger: bool
    orphaned_audit: bool
    failure_records_consistent: bool


class HealthConsistencyResponse(BaseModel):
    status: Literal["healthy", "degraded", "broken"]
    environment: str
    checked_at: str
    checks: ConsistencyChecks
    summary: str
