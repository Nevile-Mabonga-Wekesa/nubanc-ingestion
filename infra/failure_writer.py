import json
from pathlib import Path
from datetime import datetime, timezone


def write_failure(
    *,
    env: str,
    event_id: str,
    stage: str = "normalization",
    code: str = "NOT_FOUND",
    reason: str = "Raw missing event",
) -> None:
    root = Path("memory") / env / "failures"
    root.mkdir(parents=True, exist_ok=True)

    path = root / f"{event_id}.json"

    now = datetime.now(timezone.utc).isoformat()

    data = {
        "event_id": event_id,
        "failure_code": code,
        "failure_stage": stage,
        "failure_reason": reason,
        "first_occurred_at": now,
        "last_observed_at": now,
        "replay_count": 0,
        "deterministic": True,
    }

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")

