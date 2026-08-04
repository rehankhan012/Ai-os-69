import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Boolean, Float
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    slug = Column(String(500), nullable=True, unique=True)
    content = Column(Text, nullable=True)
    excerpt = Column(Text, nullable=True)
    featured_image_url = Column(Text, nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), default="draft")  # draft, review, approved, published, archived
    seo_score = Column(Float, default=0.0)
    ai_generated = Column(Boolean, default=False)
    ai_job_id = Column(UUID(as_uuid=True), ForeignKey("ai_jobs.id", ondelete="SET NULL"), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))