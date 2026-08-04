"""
Revenue Dashboard endpoints.
"""

from datetime import date, timedelta, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.revenue import Revenue
from app.models.affiliate import AffiliateLink

router = APIRouter()


@router.get("/summary")
async def get_revenue_summary(
    days: int = 30,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get revenue summary for the given period."""
    start_date = date.today() - timedelta(days=days)

    # Total revenue
    rev_result = await db.execute(
        select(
            func.coalesce(func.sum(Revenue.amount), 0),
            func.count(Revenue.id),
        ).where(Revenue.user_id == user.id, Revenue.revenue_date >= start_date)
    )
    total_revenue, revenue_count = rev_result.one()

    # Revenue by type
    type_result = await db.execute(
        select(Revenue.revenue_type, func.coalesce(func.sum(Revenue.amount), 0))
        .where(Revenue.user_id == user.id, Revenue.revenue_date >= start_date)
        .group_by(Revenue.revenue_type)
    )
    revenue_by_type = {row[0]: row[1] for row in type_result.all()}

    # Affiliate stats
    aff_result = await db.execute(
        select(
            func.coalesce(func.sum(AffiliateLink.clicks), 0),
            func.coalesce(func.sum(AffiliateLink.conversions), 0),
            func.coalesce(func.sum(AffiliateLink.estimated_earnings), 0),
            func.count(AffiliateLink.id),
        ).where(AffiliateLink.user_id == user.id, AffiliateLink.is_active == True)
    )
    aff_clicks, aff_conversions, aff_earnings, aff_count = aff_result.one()

    # Top articles by revenue
    top_result = await db.execute(
        select(Revenue.article_id, func.coalesce(func.sum(Revenue.amount), 0))
        .where(Revenue.user_id == user.id, Revenue.revenue_date >= start_date, Revenue.article_id.isnot(None))
        .group_by(Revenue.article_id)
        .order_by(func.sum(Revenue.amount).desc())
        .limit(5)
    )
    top_articles = [{"article_id": str(row[0]), "revenue": row[1]} for row in top_result.all()]

    return {
        "total_revenue": round(total_revenue, 2),
        "revenue_count": revenue_count,
        "by_type": revenue_by_type,
        "affiliate_links": aff_count,
        "affiliate_clicks": aff_clicks,
        "affiliate_conversions": aff_conversions,
        "affiliate_earnings": round(aff_earnings, 2),
        "top_articles": top_articles,
        "period_days": days,
        "currency": "USD",
    }


@router.get("/trends")
async def get_revenue_trends(
    days: int = 90,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get revenue trends over time."""
    start_date = date.today() - timedelta(days=days)

    result = await db.execute(
        select(
            Revenue.revenue_date,
            func.coalesce(func.sum(Revenue.amount), 0),
        )
        .where(Revenue.user_id == user.id, Revenue.revenue_date >= start_date)
        .group_by(Revenue.revenue_date)
        .order_by(Revenue.revenue_date)
    )
    trends = [{"date": row[0].isoformat(), "amount": row[1]} for row in result.all()]

    # Calculate monthly aggregates
    monthly = {}
    for t in trends:
        month = t["date"][:7]
        monthly[month] = monthly.get(month, 0) + t["amount"]

    return {
        "daily": trends,
        "monthly": [{"month": m, "amount": round(a, 2)} for m, a in sorted(monthly.items())],
        "period_days": days,
    }