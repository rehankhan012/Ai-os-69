import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pin_id = Column(UUID(as_uuid=True), ForeignKey("pins.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    original_url = Column(Text, nullable=True)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(50), default="image/png")
    width = Column(Integer, default=1000)
    height = Column(Integer, default=1500)
    style = Column(String(50), nullable=True)
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))