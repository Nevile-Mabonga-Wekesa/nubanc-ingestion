# Organization_db.py
import asyncpg
from contracts.api.settings import Settings

_pool = None

async def get_pool():
    global _pool
    if not _pool:
        _pool = await asyncpg.create_pool(
            Settings.DATABASE_URL,
            min_size=5,
            max_size=20
        )
    return _pool