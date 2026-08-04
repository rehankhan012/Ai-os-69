"""
Queue / Schedule endpoints.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.pin import Pin
from app.models.schedule import Schedule

router = APIRouter()


@router.get("/")
async def list_queue(
    status: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List queued items."""
    query = (
        select(Schedule, Pin)
        .join(Pin, Schedule.pin_id == Pin.id)
        .where(Schedule.user_id == user.id)
        .order_by(Schedule.scheduled_at.asc())
    )
    if status:
        query = query.where(Schedule.status == status)

    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "schedule_id": str(s.id),
            "pin_id": str(p.id),
            "title": p.title,
            "scheduled_at": s.scheduled_at.isoformat() if s.scheduled_at else None,
            "status": s.status,
        }
        for s, p in rows
    ]


@router.post("/schedule")
async def schedule_pin(
    pin_id: str,
    scheduled_at: datetime,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Schedule a pin for publication."""
    result = await db.execute(
        select(Pin).where(Pin.id == pin_id, Pin.user_id == user.id)
    )
    pin = result.scalar_one_or_none()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")

    schedule = Schedule(
        user_id=user.id,
        pin_id=pin.id,
        scheduled_at=scheduled_at,
    )
    pin.status = "queued"
    db.add(schedule)
    return {"status": "scheduled", "schedule_id": str(schedule.id)}


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_queue(
    schedule_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a scheduled item from the queue."""
    result = await db.execute(
        select(Schedule).where(Schedule.id == schedule_id, Schedule.user_id == user.id)
    )
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await db.delete(schedule)