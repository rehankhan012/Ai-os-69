"""
Keyword research endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.keyword import Keyword
from app.schemas.keyword import KeywordResearchRequest, KeywordResponse, KeywordFilterParams

router = APIRouter()


@router.get("/", response_model=list[KeywordResponse])
async def list_keywords(
    country: str | None = None,
    language: str | None = None,
    category: str | None = None,
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List saved keywords with filters."""
    query = select(Keyword).where(Keyword.user_id == user.id).order_by(Keyword.created_at.desc())

    if country:
        query = query.where(Keyword.country == country)
    if language:
        query = query.where(Keyword.language == language)
    if category:
        query = query.where(Keyword.category == category)
    if search:
        query = query.where(Keyword.keyword.ilike(f"%{search}%"))

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    keywords = result.scalars().all()
    return [KeywordResponse.model_validate(k) for k in keywords]


@router.post("/research", response_model=KeywordResponse)
async def research_keyword(
    body: KeywordResearchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Research a keyword and return AI-generated insights."""
    # TODO: Integrate with AI provider for real keyword research
    # For now, return a mock enriched result
    keyword = Keyword(
        user_id=user.id,
        keyword=body.keyword,
        category=body.category,
        language=body.language,
        country=body.country,
        search_volume=1200,
        competition_score=0.45,
        opportunity_score=0.78,
        search_intent="commercial",
        trend_direction="rising",
        related_keywords='["digital marketing", "social media tips", "content strategy"]',
        long_tail_keywords='["best pinterest strategies for 2026", "how to grow pinterest traffic organically"]',
    )
    db.add(keyword)
    await db.flush()
    await db.refresh(keyword)
    return KeywordResponse.model_validate(keyword)


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_keyword(
    keyword_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved keyword."""
    result = await db.execute(
        select(Keyword).where(Keyword.id == keyword_id, Keyword.user_id == user.id)
    )
    kw = result.scalar_one_or_none()
    if not kw:
        raise HTTPException(status_code=404, detail="Keyword not found")
    await db.delete(kw)