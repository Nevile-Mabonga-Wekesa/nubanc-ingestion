from fastapi import FastAPI
from contracts.api.config.environment import get_env
from contracts.api.routers.credit_application_v1 import router as credit_router
from contracts.api.config.env import require_env
from contracts.api.ingress.ingest_statements import routers
from contracts.api.routers import uploads, webhooks
from contracts.v1.ingest.status import router as ingest_router
from contracts.api.routers.ingest import router as ingest_router
from contracts.v1.replay import router as replay_router
from contracts.v1.ingest.failure import router as ingest_failure_router
from contracts.v1.health import router as health_router
from contracts.vendors.ingest import router as vendor_ingest_router
from contracts.api.v1.uploads.normalize import router as normalize_router
from contracts.api.v1.state.router import router as state_router
from contracts.api.v1 import replay
from contracts.api.v1 import system_health, event_trace
from contracts.api.routes_1 import router
from contracts.api.routers.org_user_invite import router as org_user_router
from contracts.api.v1.users_activate import router as users_activate_router

ENV = get_env()

require_env()

app = FastAPI(
    title="NUBANC API",
    version="1.0.0",
    description="Ingress boundary for Nubanc system",
    docs_url="/docs" if ENV != "prod" else None,
    redoc_url=None
)

app.include_router(credit_router)
app.include_router(routers)
app.include_router(uploads.router)
app.include_router(webhooks.router)
app.include_router(replay_router)
app.include_router(ingest_failure_router)
app.include_router(health_router)
app.include_router(ingest_router)
app.include_router(normalize_router)
app.include_router(state_router)
app.include_router(replay.router)
app.include_router(system_health.router)
app.include_router(event_trace.router)
app.include_router(router)
app.include_router(org_user_router, tags= ["Organizations/Users"])
app.include_router(users_activate_router, tags=["Users"])

@app.get("/__ping")
def ping():
    return {"ok": True}
