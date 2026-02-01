# events.py
import json
import asyncio

async def publish_event(event_type: str, payload: dict):
    # stub: Kafka / SQS / RabbitMQ
    asyncio.create_task(
        _fire_and_forget(event_type, payload)
    )

async def _fire_and_forget(event_type, payload):
    message = {
        "type": event_type,
        "payload": payload
    }
    print(json.dumps(message))  #Replac_e with broker
