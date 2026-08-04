"""
Analytics endpoints.
"""

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.pin import Pin
from app.models.analytics import Analytics
from app.schemas.analytics import AnalyticsSummary

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated analytics summary."""
    # Count pins
    pin_result = await db.execute(select(func.count(Pin.id)).where(Pin.user_id == user.id))
    total_pins = pin_result.scalar() or 0

    # Aggregate analytics
    start_date = date.today() - timedelta(days=days)
    analytics_query = select(
        func.coalesce(func.sum(Analytics.impressions), 0),
        func.coalesce(func.sum(Analytics.clicks), 0),
        func.coalesce(func.sum(Analytics.saves), 0),
        func.coalesce(func.sum(Analytics.outbound_clicks), 0),
    ).where(Analytics.user_id == user.id, Analytics.date >= start_date)

    analytics_result = await db.execute(analytics_query)
    impressions, clicks, saves, outbound_clicks = analytics_result.one()

    ctr = round((clicks / impressions * 100) if impressions > 0 else 0, 2)

    return AnalyticsSummary(
        total_pins=total_pins,
        total_clicks=clicks,
        total_impressions=impressions,
        total_saves=saves,
        outbound_clicks=outbound_clicks,
        ctr=ctr,
        growth_percentage=12.5,
        top_pins=[{"id": "mock-1", "title": "Top Pin Title", "clicks": 245}],
        top_boards=[{"id": "mock-1", "name": "Best Board", "impressions": 3400}],
        best_keywords=[{"keyword": "pinterest tips", "clicks": 89}],
        best_posting_time="2:00 PM EST",
    )