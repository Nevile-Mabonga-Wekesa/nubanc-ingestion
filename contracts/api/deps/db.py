from typing import Generator
from contracts.api.db.session import SessionLocal

def get_db_conn() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
