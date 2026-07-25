import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class MediaHistory(Base):
    """Relational record of every analyzed upload."""

    __tablename__ = "media_history"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    file_hash = Column(String(64), unique=True, index=True)
    media_type = Column(String(20), default="image")
    nsfw_status = Column(String(50))
    nsfw_score = Column(Float)
    is_nsfw = Column(Boolean, default=False)
    embedding = Column(JSON)  # 512-dimension CLIP vector stored as a JSON array.
    uploaded_by = Column(String(100), default="anonymous")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
