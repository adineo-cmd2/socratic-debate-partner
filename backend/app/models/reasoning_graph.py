from datetime import datetime
from typing import Any

from sqlalchemy import Integer, ForeignKey, DateTime, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReasoningGraph(Base):
    __tablename__ = "reasoning_graphs"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("debate_sessions.id"), unique=True, index=True)
    data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
