import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float, Boolean
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class Pin(Base):
    __tablename__ = "pins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    board_id = Column(UUID(as_uuid=True), ForeignKey("boards.id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    link = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    alt_text = Column(Text, nullable=True)
    seo_score = Column(Float, default=0.0)
    status = Column(String(50), default="draft")  # draft, queued, published, archived
    is_generated = Column(Boolean, default=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))