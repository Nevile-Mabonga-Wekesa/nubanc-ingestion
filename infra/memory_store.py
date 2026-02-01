# contracts/infra/memory_store.py
from pathlib import Path
import json
import uuid
from datetime import datetime, timezone

BASE_PATH = Path("memory")

def write_event(env: str, event: dict, folder: str) -> str:
    """Write event or normalized event in memory store."""
    event_id = f"nevt_{uuid.uuid4().hex}"
    event["event_id"] = event_id
    event["occurred_at"] = datetime.now(timezone.utc).isoformat()
    path = BASE_PATH / env / folder
    path.mkdir(parents=True, exist_ok=True)
    (path / f"{event_id}.json").write_text(json.dumps(event, indent=2), encoding="utf-8")
    return event_id

def read_event(env: str, folder: str, event_id: str) -> dict:
    path = BASE_PATH / env / folder / f"{event_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Event {event_id} not found")
    return json.loads(path.read_text(encoding="utf-8"))
