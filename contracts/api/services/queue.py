import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def push_to_queue(file_id: str):
    r.lpush("ingestion_queue", file_id)

def pop_from_queue():
    data = r.rpop("ingestion_queue")
    if data:
        return data.decode("utf-8")
    return None
