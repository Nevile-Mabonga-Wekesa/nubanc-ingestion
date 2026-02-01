from fastapi import APIRouter, Request, Header, HTTPException
import hmac, hashlib
from ..services.queue import push_to_queue
import json
from uuid import uuid4

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

SECRET_KEY = b"supersecret"  # Use environment variable in prod


@router.post("/bank-feed")
async def bank_feed(request: Request, x_signature: str = Header(...)):
    body = await request.body()
    # Verify HMAC signature
    computed_sig = hmac.new(SECRET_KEY, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed_sig, x_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    data = await request.json()
    file_id = str(uuid4())

    # Save payload as JSON file
    with open(f"./uploads/raw/{file_id}.json", "w") as f:
        json.dump(data, f)

    # Push to queue
    push_to_queue(file_id)

    return {"status": "queued", "file_id": file_id}
