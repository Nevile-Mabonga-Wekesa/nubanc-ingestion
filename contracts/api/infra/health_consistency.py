from pathlib import Path
from datetime import datetime, timezone
from typing import Set

from contracts.api.schemas.v1.health import (
    HealthConsistencyResponse,
    ConsistencyChecks,
)


class HealthConsistencyChecker:
    def __init__(self, *, base_path: Path, env: str):
        if not env:
            raise RuntimeError("NUBANC_ENV must be set")

        self.env = env
        self.root = base_path / env

        self.raw = self.root / "raw"
        self.ledger = self.root / "ledger"
        self.audit = self.root / "audit"
        self.failures = self.root / "failures"

    @staticmethod
    def _event_ids(path: Path) -> Set[str]:
        if not path.exists():
            return set()

        return {
            p.stem
            for p in path.rglob("*.json")
            if p.is_file()
        }

    def check(self) -> HealthConsistencyResponse:
        raw_ids = self._event_ids(self.raw)
        ledger_ids = self._event_ids(self.ledger)
        audit_ids = self._event_ids(self.audit)
        failure_ids = self._event_ids(self.failures)

        missing_ledger = raw_ids - ledger_ids
        missing_audit = raw_ids - audit_ids

        orphaned_ledger = bool(ledger_ids - raw_ids)
        orphaned_audit = bool(audit_ids - raw_ids)

        failure_consistent = failure_ids.issubset(raw_ids)

        checks = ConsistencyChecks(
            raw_vs_ledger="ok" if not missing_ledger else "missing_ledger_entries",
            raw_vs_audit="ok" if not missing_audit else "missing_audit_entries",
            orphaned_ledger=orphaned_ledger,
            orphaned_audit=orphaned_audit,
            failure_records_consistent=failure_consistent,
        )

        if (
            not missing_ledger
            and not missing_audit
            and not orphaned_ledger
            and not orphaned_audit
            and failure_consistent
        ):
            status = "healthy"
            summary = "All invariants satisfied"
        elif failure_consistent:
            status = "degraded"
            summary = "Derived state incomplete but explainable"
        else:
            status = "broken"
            summary = "Inconsistent failure or orphaned state detected"

        return HealthConsistencyResponse(
            status=status,
            environment=self.env,
            checked_at=datetime.now(timezone.utc).isoformat(),
            checks=checks,
            summary=summary,
        )
