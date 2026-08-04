import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float, Boolean
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class AffiliateLink(Base):
    __tablename__ = "affiliate_links"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="SET NULL"), nullable=True)
    pin_id = Column(UUID(as_uuid=True), ForeignKey("pins.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    network = Column(String(100), nullable=True)  # Amazon, ShareASale, Impact, etc.
    commission_rate = Column(Float, default=0.0)
    estimated_earnings = Column(Float, default=0.0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))