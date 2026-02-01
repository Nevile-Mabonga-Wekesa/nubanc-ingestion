from sqlalchemy import create_engine, Column, String, DateTime, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum
from datetime import datetime

DATABASE_URL = "sqlite:///./files.db"  # for simplicity
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FileStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    done = "done"
    failed = "failed"

class FileRecord(Base):
    __tablename__ = "file_records"

    file_id = Column(String, primary_key=True, index=True)
    file_type = Column(String)
    uploader = Column(String)
    status = Column(Enum(FileStatus), default=FileStatus.queued)
    extra_metadata = Column("metadata", JSON)
    errors = Column(JSON, default= list)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)
