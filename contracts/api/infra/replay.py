import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any
from contracts.api.schemas.v1.replay import ReplayRequest, ReplayResponse


class ReplayEventError(ValueError):
    """Custom exception for invalid replay events."""
    pass


class ReplayEngine:
    def __init__(self, *, base_path: Path, env: str):
        if not env:
            raise RuntimeError("NUBANC_ENV must be set")

        self.env = env
        self.root = base_path / env

        self.raw = self.root / "raw"
        self.ledger = self.root / "ledger"
        self.audit = self.root / "audit"

        # Ensure directories exist
        self.ledger.mkdir(parents=True, exist_ok=True)
        self.audit.mkdir(parents=True, exist_ok=True)

    def _load_raw_events(self) -> List[Path]:
        """Load all raw JSON event files, sorted by path."""
        return sorted(self.raw.rglob("*.json"))

    @staticmethod
    def validate_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure all mandatory keys exist.
        Auto-generate 'event_id' if missing for resilience.
        """
        required_keys = ["event_id", "tenant_id", "event_type", "timestamp", "payload"]

        missing_keys = [key for key in required_keys if key not in event]

        # Auto-generate event_id if missing
        if "event_id" in missing_keys:
            event["event_id"] = f"evt_{uuid.uuid4().hex}"
            missing_keys.remove("event_id")

        if missing_keys:
            raise ReplayEventError(
                f"Invalid replay event: missing {missing_keys}. "
                f"Received keys: {list(event.keys())}"
            )

        return event

    def replay(self, request: ReplayRequest) -> ReplayResponse:
        """
        Replays all events from the raw folder.
        If dry_run is True, ledger/audit are not updated.
        """
        replay_id = f"rpl_{uuid.uuid4().hex}"
        started_at = datetime.now(timezone.utc)

        events = self._load_raw_events()
        scanned = len(events)
        replayed = 0

        for event_file in events:
            with event_file.open("r", encoding="utf-8") as f:
                event = json.load(f)

            # Validate & enrich event
            try:
                event = self.validate_event(event)
            except ReplayEventError as e:
                # Optional: log and skip instead of failing
                print(f"[WARNING] Skipping invalid event {event_file}: {str(e)}")
                continue

            if not request.dry_run:
                ledger_path = self.ledger / f"{event['event_id']}.json"
                audit_path = self.audit / f"{event['event_id']}.json"

                ledger_path.write_text(json.dumps(event, indent=2))
                audit_path.write_text(json.dumps({
                    "event_id": event["event_id"],
                    "event_type": event["event_type"],
                    "replayed_at": datetime.now(timezone.utc).isoformat()
                }, indent=2))

            replayed += 1

        completed_at = datetime.now(timezone.utc)

        return ReplayResponse(
            replay_id=replay_id,
            events_scanned=scanned,
            events_replayed=replayed,
            status="completed",
            started_at=started_at.isoformat(),
            completed_at=completed_at.isoformat(),
        )


# --- Public API function ---
def replay(request: Dict[str, Any], engine: ReplayEngine) -> ReplayResponse:
    """
    Handles replay request from external callers.
    Converts raw dict to ReplayRequest and delegates to engine.
    """
    # Ensure required request keys exist
    if "dry_run" not in request:
        request["dry_run"] = False

    replay_request = ReplayRequest(**request)
    return engine.replay(replay_request)
