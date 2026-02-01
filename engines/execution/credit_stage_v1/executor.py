import json
import hashlib
from pathlib import Path

ENV = os.environ["NUBANC_ENV"]
AUDIT_PATH = Path(f"memory/{ENV}/audit")
LEDGER_PATH = Path(f"memory/{ENV}/ledger")

def load_decisions():
    decisions = []
    for file in LEDGER_PATH.glob("*.json"):
        with open(file) as f:
            decisions.append(json.load(f))
    return decisions

def simulate_execution(decision):
    """
    This simulates execution.
    No side effects.
    No external calls.
    """
    execution_result = {
        "execution_name": "execution.credit_stage.v1",
        "decision_id": decision["decision_id"],
        "tenant_id": decision["tenant_id"],
        "action": f"assign_{decision['result']}",
        "status": "simulated_success"
    }

    return execution_result

def write_audit(execution):
    audit_id_source = f"{execution['decision_id']}:{execution['action']}"
    audit_id = hashlib.sha256(audit_id_source.encode()).hexdigest()

    record = {
        "audit_id": audit_id,
        "execution": execution
    }

    AUDIT_PATH.mkdir(parents=True, exist_ok=True)
    file_path = AUDIT_PATH / f"{audit_id}.json"

    if file_path.exists():
        return  # idempotent

    with open(file_path, "w") as f:
        json.dump(record, f, indent=2)

def run_execution_engine():
    decisions = load_decisions()

    for decision in decisions:
        execution = simulate_execution(decision)
        write_audit(execution)

if __name__ == "__main__":
    run_execution_engine()
