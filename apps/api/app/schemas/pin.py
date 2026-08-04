from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import UuidStr


class PinCreate(BaseModel):
    title: str
    description: str | None = None
    link: str | None = None
    board_id: str | None = None
    alt_text: str | None = None
    status: str = "draft"
    scheduled_at: datetime | None = None


class PinUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    link: str | None = None
    board_id: str | None = None
    image_url: str | None = None
    alt_text: str | None = None
    status: str | None = None
    scheduled_at: datetime | None = None


class PinResponse(BaseModel):
    id: UuidStr
    board_id: UuidStr | None = None
    title: str
    description: str | None = None
    link: str | None = None
    image_url: str | None = None
    alt_text: str | None = None
    seo_score: float
    status: str
    is_generated: bool
    scheduled_at: datetime | None = None
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}