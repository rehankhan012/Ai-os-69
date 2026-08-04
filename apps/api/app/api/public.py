"""
Public website API — powers the public blog at darkverse.co.in.

Read-only, NO authentication. Only exposes PUBLISHED articles (never drafts,
review, or archived). The public site never touches agents, bots, analytics,
or admin data — just articles and categories.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.config import settings
from app.models.article import Article
from app.models.category import Category

router = APIRouter()


def _article_public(a: Article, category: Category | None = None) -> dict:
    """Serialize a published article for the public site."""
    return {
        "id": str(a.id),
        "title": a.title,
        "slug": a.slug or a.id.hex,
        "excerpt": a.excerpt,
        "content": a.content,
        "featured_image_url": a.featured_image_url,
        "seo_score": a.seo_score,
        "view_count": a.view_count,
        "reading_time_minutes": _reading_time(a.content),
        "published_at": a.published_at.isoformat() if a.published_at else None,
        "category": {
            "name": category.name,
            "slug": category.slug or category.name.lower().replace(" ", "-"),
            "color": category.color,
        }
        if category
        else None,
    }


def _reading_time(content: str | None) -> int:
    """Rough reading time in minutes based on word count."""
    if not content:
        return 1
    words = len(content.replace("<", " <").split())
    return max(1, round(words / 200))


@router.get("/site")
async def site_info():
    """Public site branding + feature flags for the website."""
    return {
        "name": settings.site_name,
        "tagline": settings.site_tagline,
        "description": settings.site_description,
    }


@router.get("/articles")
async def list_published_articles(
    category: str | None = None,
    search: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List published articles (newest first). Optional category/search filters."""
    query = (
        select(Article, Category)
        .outerjoin(Category, Category.id == Article.category_id)
        .where(Article.status == "published")
        .order_by(Article.published_at.desc().nulls_last(), Article.updated_at.desc())
    )

    if category:
        query = query.where(
            (Category.slug == category) | (Category.name.ilike(f"%{category}%"))
        )
    if search:
        query = query.where(
            (Article.title.ilike(f"%{search}%"))
            | (Article.excerpt.ilike(f"%{search}%"))
        )

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    rows = result.all()

    # Total for pagination metadata
    total = await db.execute(
        select(func.count(Article.id)).where(Article.status == "published")
    )

    return {
        "articles": [_article_public(a, c) for a, c in rows],
        "total": total.scalar() or 0,
        "limit": limit,
        "offset": offset,
    }


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Public categories (only those with at least one published article)."""
    result = await db.execute(
        select(Category)
        .where(Category.article_count > 0)
        .order_by(Category.name)
    )
    return [
        {
            "name": c.name,
            "slug": c.slug or c.name.lower().replace(" ", "-"),
            "color": c.color,
            "article_count": c.article_count,
        }
        for c in result.scalars().all()
    ]


@router.get("/articles/{slug}")
async def get_published_article(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a single published article by slug, bumping its view count."""
    result = await db.execute(
        select(Article, Category)
        .outerjoin(Category, Category.id == Article.category_id)
        .where(
            Article.status == "published",
            (Article.slug == slug) | (Article.id == slug),
        )
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Article not found")
    article, category = row

    # Track a view (best-effort)
    try:
        article.view_count = (article.view_count or 0) + 1
        await db.flush()
    except Exception:
        pass

    return _article_public(article, category)
