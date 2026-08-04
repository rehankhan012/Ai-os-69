"""
User settings endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.setting import Setting

router = APIRouter()


@router.get("/")
async def get_settings(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get all settings for the authenticated user."""
    result = await db.execute(select(Setting).where(Setting.user_id == user.id))
    settings = result.scalars().all()
    return {s.key: s.value for s in settings}


@router.put("/")
async def update_settings(
    body: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upsert settings for the authenticated user."""
    for key, value in body.items():
        result = await db.execute(
            select(Setting).where(Setting.user_id == user.id, Setting.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = str(value)
        else:
            db.add(Setting(user_id=user.id, key=key, value=str(value)))

    return {"status": "saved"}


@router.get("/ai")
async def get_ai_settings(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Get AI-specific settings."""
    result = await db.execute(
        select(Setting).where(Setting.user_id == user.id, Setting.category == "ai")
    )
    settings = result.scalars().all()
    return {s.key: s.value for s in settings}