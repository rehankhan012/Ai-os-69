import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Float, Date
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class Analytics(Base):
    __tablename__ = "analytics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pin_id = Column(UUID(as_uuid=True), ForeignKey("pins.id", ondelete="CASCADE"), nullable=True)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id", ondelete="SET NULL"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    impressions = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    outbound_clicks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))