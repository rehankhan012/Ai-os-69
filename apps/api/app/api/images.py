"""
Image storage endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.image import Image

router = APIRouter()


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image file."""
    # TODO: Implement actual file storage (local or S3)
    image = Image(
        user_id=user.id,
        filename=file.filename or "untitled.png",
        storage_path=f"uploads/{user.id}/{file.filename}",
        mime_type=file.content_type or "image/png",
    )
    db.add(image)
    await db.flush()
    await db.refresh(image)
    return {"id": str(image.id), "filename": image.filename, "storage_path": image.storage_path}


@router.get("/")
async def list_images(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List uploaded images."""
    result = await db.execute(
        select(Image).where(Image.user_id == user.id).order_by(Image.created_at.desc())
    )
    images = result.scalars().all()
    return [
        {
            "id": str(img.id),
            "filename": img.filename,
            "style": img.style,
            "width": img.width,
            "height": img.height,
            "created_at": img.created_at.isoformat(),
        }
        for img in images
    ]