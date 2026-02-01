from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class FileStatus(enum.Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class FileRecord(Base):
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    status = Column(Enum(FileStatus), nullable=False)
