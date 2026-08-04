from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import UuidStr


class BoardCreate(BaseModel):
    name: str
    description: str | None = None
    is_private: bool = False


class BoardUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cover_image_url: str | None = None
    is_private: bool | None = None


class BoardResponse(BaseModel):
    id: UuidStr
    name: str
    description: str | None = None
    cover_image_url: str | None = None
    is_private: bool
    pin_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}