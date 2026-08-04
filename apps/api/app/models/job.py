import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Boolean, Float
from app.core.db_types import Uuid as UUID

from app.core.database import Base


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(String(100), nullable=False, index=True)  # content_generation, graphic_rendering, seo_analysis, trend_scan
    status = Column(String(50), default="queued")  # queued, running, completed, failed
    input_data = Column(Text, nullable=True)  # JSON
    output_data = Column(Text, nullable=True)  # JSON
    progress = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))