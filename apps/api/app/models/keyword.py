import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    keyword = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    language = Column(String(10), default="en")
    country = Column(String(10), default="US")
    search_volume = Column(Integer, nullable=True)
    competition_score = Column(Float, nullable=True)
    opportunity_score = Column(Float, nullable=True)
    search_intent = Column(String(50), nullable=True)  # informational, commercial, transactional, navigational
    trend_direction = Column(String(20), nullable=True)  # rising, stable, falling
    related_keywords = Column(Text, nullable=True)  # JSON array
    long_tail_keywords = Column(Text, nullable=True)  # JSON array
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))