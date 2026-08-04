"""
Board CRUD endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.board import Board
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse

router = APIRouter()


@router.get("/", response_model=list[BoardResponse])
async def list_boards(
    search: str | None = None,
    sort: str = "updated_at",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all boards for the authenticated user."""
    query = select(Board).where(Board.user_id == user.id).order_by(Board.updated_at.desc())

    if search:
        query = query.where(Board.name.ilike(f"%{search}%"))

    result = await db.execute(query)
    boards = result.scalars().all()
    return [BoardResponse.model_validate(b) for b in boards]


@router.post("/", response_model=BoardResponse, status_code=status.HTTP_201_CREATED)
async def create_board(
    body: BoardCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new board."""
    board = Board(
        user_id=user.id,
        name=body.name,
        description=body.description,
        is_private=int(body.is_private),
    )
    db.add(board)
    await db.flush()
    await db.refresh(board)
    return BoardResponse.model_validate(board)


@router.get("/{board_id}", response_model=BoardResponse)
async def get_board(
    board_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single board by ID."""
    result = await db.execute(
        select(Board).where(Board.id == board_id, Board.user_id == user.id)
    )
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return BoardResponse.model_validate(board)


@router.patch("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: str,
    body: BoardUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a board."""
    result = await db.execute(
        select(Board).where(Board.id == board_id, Board.user_id == user.id)
    )
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    update_data = body.model_dump(exclude_unset=True)
    if "is_private" in update_data:
        update_data["is_private"] = int(update_data["is_private"])

    for key, value in update_data.items():
        setattr(board, key, value)

    await db.flush()
    await db.refresh(board)
    return BoardResponse.model_validate(board)


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a board."""
    result = await db.execute(
        select(Board).where(Board.id == board_id, Board.user_id == user.id)
    )
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    await db.delete(board)