import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Boolean
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class PublishingQueue(Base):
    __tablename__ = "publishing_queue"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="SET NULL"), nullable=True)
    pin_id = Column(UUID(as_uuid=True), ForeignKey("pins.id", ondelete="SET NULL"), nullable=True)
    graphic_id = Column(UUID(as_uuid=True), ForeignKey("graphics.id", ondelete="SET NULL"), nullable=True)
    content_type = Column(String(50), nullable=False)  # article, pin, graphic
    status = Column(String(50), default="draft")  # draft, pending_review, approved, queued, publishing, published, failed
    requires_approval = Column(Boolean, default=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))