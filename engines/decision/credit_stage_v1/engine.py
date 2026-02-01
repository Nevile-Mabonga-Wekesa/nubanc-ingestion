import json
import hashlib
from pathlib import Path
from replay.replay_engine import load_events

ENV = os.environ["NUBANC_ENV"]
LEDGER_PATH = Path(f"memory/{ENV}/ledger")

def compute_credit_stage(events):
    """
    Extremely simple deterministic rule:
    - If tenant has >= 1 event → stage_1
    This is placeholder logic to prove structure, not business value.
    """
    tenant_event_count = {}

    for event in events:
        tenant = event["tenant_id"]
        tenant_event_count[tenant] = tenant_event_count.get(tenant, 0) + 1

    decisions = []

    for tenant, count in tenant_event_count.items():
        stage = "stage_1" if count >= 1 else "unknown"

        decision = {
            "decision_name": "decision.credit_stage.v1",
            "tenant_id": tenant,
            "computed_stage": stage,
            "input_event_count": count
        }

        decisions.append(decision)

    return decisions

def write_decision(decision):
    decision_id_source = f"{decision['tenant_id']}:{decision['decision_name']}:{decision['computed_stage']}"
    decision_id = hashlib.sha256(decision_id_source.encode()).hexdigest()

    record = {
        "decision_id": decision_id,
        "decision_name": decision["decision_name"],
        "tenant_id": decision["tenant_id"],
        "result": decision["computed_stage"],
        "inputs": {
            "event_count": decision["input_event_count"]
        }
    }

    LEDGER_PATH.mkdir(parents=True, exist_ok=True)
    file_path = LEDGER_PATH / f"{decision_id}.json"

    if file_path.exists():
        return  # idempotent: decision already recorded

    with open(file_path, "w") as f:
        json.dump(record, f, indent=2)

def run_decision_engine():
    events = load_events()
    decisions = compute_credit_stage(events)

    for decision in decisions:
        write_decision(decision)

if __name__ == "__main__":
    run_decision_engine()
