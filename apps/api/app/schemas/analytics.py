from datetime import date, datetime

from pydantic import BaseModel

from app.schemas.common import UuidStr


class AnalyticsResponse(BaseModel):
    id: UuidStr
    pin_id: UuidStr | None = None
    board_id: UuidStr | None = None
    date: date
    impressions: int
    saves: int
    clicks: int
    outbound_clicks: int

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    total_pins: int = 0
    total_clicks: int = 0
    total_impressions: int = 0
    total_saves: int = 0
    outbound_clicks: int = 0
    ctr: float = 0.0
    growth_percentage: float = 0.0
    top_pins: list[dict] = []
    top_boards: list[dict] = []
    best_keywords: list[dict] = []
    best_posting_time: str | None = None


class AnalyticsDateRange(BaseModel):
    start_date: date
    end_date: date