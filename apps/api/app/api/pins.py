"""
Pin CRUD endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.pin import Pin
from app.schemas.pin import PinCreate, PinUpdate, PinResponse

router = APIRouter()


@router.get("/", response_model=list[PinResponse])
async def list_pins(
    status: str | None = None,
    board_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List pins for the authenticated user."""
    query = select(Pin).where(Pin.user_id == user.id).order_by(Pin.created_at.desc())

    if status:
        query = query.where(Pin.status == status)
    if board_id:
        query = query.where(Pin.board_id == board_id)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    pins = result.scalars().all()
    return [PinResponse.model_validate(p) for p in pins]


@router.post("/", response_model=PinResponse, status_code=status.HTTP_201_CREATED)
async def create_pin(
    body: PinCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new pin."""
    pin = Pin(
        user_id=user.id,
        **body.model_dump(exclude_unset=True),
    )
    db.add(pin)
    await db.flush()
    await db.refresh(pin)
    return PinResponse.model_validate(pin)


@router.get("/{pin_id}", response_model=PinResponse)
async def get_pin(
    pin_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single pin."""
    result = await db.execute(
        select(Pin).where(Pin.id == pin_id, Pin.user_id == user.id)
    )
    pin = result.scalar_one_or_none()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    return PinResponse.model_validate(pin)


@router.patch("/{pin_id}", response_model=PinResponse)
async def update_pin(
    pin_id: str,
    body: PinUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a pin."""
    result = await db.execute(
        select(Pin).where(Pin.id == pin_id, Pin.user_id == user.id)
    )
    pin = result.scalar_one_or_none()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(pin, key, value)

    await db.flush()
    await db.refresh(pin)
    return PinResponse.model_validate(pin)


@router.delete("/{pin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pin(
    pin_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a pin."""
    result = await db.execute(
        select(Pin).where(Pin.id == pin_id, Pin.user_id == user.id)
    )
    pin = result.scalar_one_or_none()
    if not pin:
        raise HTTPException(status_code=404, detail="Pin not found")
    await db.delete(pin)