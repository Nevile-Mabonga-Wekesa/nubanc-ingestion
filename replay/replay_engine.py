import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# -------------------------
# ENVIRONMENT SETUP
# -------------------------
def load_env(env_var: str = "NUBANC_ENV") -> str:
    """Load required environment variable or exit."""
    try:
        return os.environ[env_var]
    except KeyError:
        print(f"ERROR: {env_var} is not set. Aborting replay.", file=sys.stderr)
        sys.exit(1)


ENV = load_env()

RAW_MEMORY_PATH = Path(f"memory/{ENV}/raw")
LEDGER_PATH = Path(f"memory/{ENV}/ledger")
AUDIT_PATH = Path(f"memory/{ENV}/audit")


# -------------------------
# RAW DATA SEEDING
# -------------------------
def seed_raw_data(path: Path) -> None:
    """Seed initial raw data for cold-start environments."""
    path.mkdir(parents=True, exist_ok=True)
    year_dir = path / "2025"
    year_dir.mkdir(exist_ok=True)
    file_path = year_dir / "0001_initial_event.json"

    if not file_path.exists():
        file_path.write_text(
            json.dumps({
                "tenant_id": "default_tenant",
                "event_type": "init",
                "timestamp": "2025-12-20T00:00:00Z",
                "payload": {}
            })
        )
        print(f"Seeded raw data at {file_path}")


# -------------------------
# EVENT LOADING
# -------------------------
def load_events(path: Path) -> List[Dict[str, Any]]:
    """Load all events from the raw memory path."""
    events: List[Dict[str, Any]] = []

    for year in sorted(path.iterdir()):
        if not year.is_dir():
            continue
        for file in sorted(year.iterdir()):
            if not file.is_file():
                continue
            try:
                with open(file) as f:
                    event_data = json.load(f)
                    events.append(event_data)
            except json.JSONDecodeError as e:
                print(f"WARNING: Skipping invalid JSON file {file}: {e}")

    return events


# -------------------------
# REPLAY LOGIC
# -------------------------
def replay() -> Dict[str, Any]:
    """Process raw events and generate ledger/audit state."""
    # Cold-start: seed raw data if missing
    if not RAW_MEMORY_PATH.exists() or not any(RAW_MEMORY_PATH.iterdir()):
        print(f"No raw data found in {RAW_MEMORY_PATH}. Seeding initial event...")
        seed_raw_data(RAW_MEMORY_PATH)

    events = load_events(RAW_MEMORY_PATH)

    if not events:
        print(f"ERROR: No events found in {RAW_MEMORY_PATH}. Cannot regenerate ledger/audit.", file=sys.stderr)
        sys.exit(1)

    state = {
        "event_count": 0,
        "tenants": set()
    }

    for event in events:
        state["event_count"] += 1
        tenant_id = event.get("tenant_id")
        if tenant_id:
            state["tenants"].add(tenant_id)
        else:
            print(f"WARNING: event missing tenant_id, skipping: {event}")

    return {
        "total_events": state["event_count"],
        "tenants_seen": sorted(list(state["tenants"]))
    }


# -------------------------
# SCRIPT ENTRYPOINT
# -------------------------
if __name__ == "__main__":
    result = replay()
    print(json.dumps(result, indent=2))
