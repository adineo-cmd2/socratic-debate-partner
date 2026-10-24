from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FallacyRecord(Base):
    __tablename__ = "fallacy_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("debate_sessions.id"), index=True)
    message_id: Mapped[int] = mapped_column(Integer, ForeignKey("reasoning_messages.id"), index=True, nullable=True)
    fallacy_type: Mapped[str] = mapped_column(String(100))
    snippet: Mapped[str] = mapped_column(String(1000))
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
