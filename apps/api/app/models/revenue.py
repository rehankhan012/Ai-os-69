import uuid
from datetime import datetime, timezone, date

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float, Date
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class Revenue(Base):
    __tablename__ = "revenue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    revenue_type = Column(String(50), nullable=False, index=True)  # affiliate, digital_product, advertising, manual
    source = Column(String(255), nullable=True)  # amazon, shareasale, direct, etc.
    amount = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    commission_rate = Column(Float, default=0.0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="SET NULL"), nullable=True)
    pin_id = Column(UUID(as_uuid=True), ForeignKey("pins.id", ondelete="SET NULL"), nullable=True)
    revenue_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))