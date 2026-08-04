import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float, Boolean
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class Graphic(Base):
    __tablename__ = "graphics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="SET NULL"), nullable=True)
    pin_id = Column(UUID(as_uuid=True), ForeignKey("pins.id", ondelete="SET NULL"), nullable=True)
    template_name = Column(String(100), nullable=False)
    variation = Column(String(10), default="A")
    svg_content = Column(Text, nullable=True)
    png_path = Column(String(500), nullable=True)
    design_spec = Column(Text, nullable=True)  # JSON of the design spec
    quality_score = Column(Float, default=0.0)
    width = Column(Integer, default=1000)
    height = Column(Integer, default=1500)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))