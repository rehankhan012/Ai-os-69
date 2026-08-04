from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import UuidStr


class KeywordResearchRequest(BaseModel):
    keyword: str
    category: str | None = None
    language: str = "en"
    country: str = "US"


class KeywordResponse(BaseModel):
    id: UuidStr
    keyword: str
    category: str | None = None
    language: str | None = None
    country: str | None = None
    search_volume: int | None = None
    competition_score: float | None = None
    opportunity_score: float | None = None
    search_intent: str | None = None
    trend_direction: str | None = None
    related_keywords: list[str] | None = None
    long_tail_keywords: list[str] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class KeywordFilterParams(BaseModel):
    country: str | None = None
    language: str | None = None
    category: str | None = None
    search: str | None = None
    limit: int = 20
    offset: int = 0