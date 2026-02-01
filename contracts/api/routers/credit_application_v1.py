from fastapi import APIRouter
from contracts.api.config.environment import get_env

router = APIRouter()

ENV = get_env()

@router.post("/applications", status_code=202)
def submit_credit_application():
    event_path = emit_credit_application()

    return {
        "status": "accepted",
        "environment": ENV,
        "event_path": str(event_path)
    }
