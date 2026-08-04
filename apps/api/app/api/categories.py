"""
Category and Tag management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.category import Category
from app.models.tag import Tag

router = APIRouter()


@router.get("/categories")
async def list_categories(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all categories."""
    result = await db.execute(
        select(Category).where(Category.user_id == user.id).order_by(Category.name)
    )
    categories = result.scalars().all()
    return [
        {"id": str(c.id), "name": c.name, "slug": c.slug, "color": c.color, "article_count": c.article_count}
        for c in categories
    ]


@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(
    name: str,
    color: str = "#6366F1",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new category."""
    category = Category(user_id=user.id, name=name, color=color)
    db.add(category)
    await db.flush()
    await db.refresh(category)
    return {"id": str(category.id), "name": category.name, "color": category.color}


@router.get("/tags")
async def list_tags(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all tags."""
    result = await db.execute(
        select(Tag).where(Tag.user_id == user.id).order_by(Tag.name)
    )
    tags = result.scalars().all()
    return [{"id": str(t.id), "name": t.name, "slug": t.slug} for t in tags]


@router.post("/tags", status_code=status.HTTP_201_CREATED)
async def create_tag(
    name: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new tag."""
    tag = Tag(user_id=user.id, name=name)
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return {"id": str(tag.id), "name": tag.name}