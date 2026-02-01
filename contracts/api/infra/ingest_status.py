import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from contracts.api.schemas.v1.ingest.status import (
    IngestStatusResponse,
    ArtifactStatus,
    FailureInfo,
)


class IngestStatusReader:
    def __init__(self, *, base_path: Path, env: str):
        if not env:
            raise RuntimeError("NUBANC_ENV must be set")

        self.env = env
        self.root = base_path / env

        self.raw_path = self.root / "raw"
        self.ledger_path = self.root / "ledger"
        self.audit_path = self.root / "audit"

    @staticmethod
    def _find_event(root: Path, event_id: str) -> Optional[Path]:
        for path in root.rglob(f"*{event_id}*.json"):
            return path
        return None

    def read(self, *, event_id: str) -> IngestStatusResponse:
        raw_file = self._find_event(self.raw_path, event_id)

        if not raw_file:
            raise FileNotFoundError(event_id)

        ledger_file = self._find_event(self.ledger_path, event_id)
        audit_file = self._find_event(self.audit_path, event_id)

        with raw_file.open("r", encoding="utf-8") as f:
            raw = json.load(f)

        artifacts = ArtifactStatus(
            raw_event=True,
            ledger_entry=ledger_file is not None,
            audit_entry=audit_file is not None,
        )

        if artifacts.ledger_entry and artifacts.audit_entry:
            status = "processed"
        else:
            status = "accepted"

        received_at = raw.get("occurred_at")
        last_updated = max(
            p.stat().st_mtime
            for p in [raw_file, ledger_file, audit_file]
            if p is not None
        )

        return IngestStatusResponse(
            event_id=event_id,
            event_type=raw["event_type"],
            status=status,
            received_at=received_at,
            last_updated_at=datetime.utcfromtimestamp(last_updated).isoformat() + "Z",
            environment=self.env,
            artifacts=artifacts,
            failure=None,
        )