from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(10), default='USER')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AnalysisRecord(Base):
    __tablename__ = 'analysis_records'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(10))
    file_url: Mapped[str] = mapped_column(String(500))
    storage_path: Mapped[str] = mapped_column(String(1000))
    analysis_type: Mapped[str] = mapped_column(String(20))
    score_safe: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    score_explicit: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    score_suggestive: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    score_gore: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    text_flag_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vector_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    matched_record_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    similarity_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    ai_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_status: Mapped[str] = mapped_column(String(10), default='REVIEW', index=True)
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class PlatformMetric(Base):
    __tablename__ = 'platform_metrics'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    metric_key: Mapped[str] = mapped_column(String(50), unique=True)
    metric_value: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(80))
    details: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
