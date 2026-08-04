"""
Media Library endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.media import Media

router = APIRouter()


@router.get("/")
async def list_media(
    media_type: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all media assets."""
    query = select(Media).where(Media.user_id == user.id).order_by(Media.created_at.desc())
    if media_type:
        query = query.where(Media.media_type == media_type)
    result = await db.execute(query)
    items = result.scalars().all()
    return [
        {
            "id": str(m.id),
            "filename": m.filename,
            "original_name": m.original_name,
            "mime_type": m.mime_type,
            "media_type": m.media_type,
            "width": m.width,
            "height": m.height,
            "file_size": m.file_size,
            "alt_text": m.alt_text,
            "created_at": m.created_at.isoformat(),
        }
        for m in items
    ]


@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    media_type: str = "image",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a media asset."""
    media = Media(
        user_id=user.id,
        filename=file.filename or "untitled",
        original_name=file.filename or "untitled",
        storage_path=f"uploads/{user.id}/{file.filename}",
        mime_type=file.content_type or "image/png",
        media_type=media_type,
    )
    db.add(media)
    await db.flush()
    await db.refresh(media)
    return {"id": str(media.id), "filename": media.filename, "media_type": media.media_type}


@router.delete("/{media_id}", status_code=204)
async def delete_media(
    media_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a media asset."""
    result = await db.execute(
        select(Media).where(Media.id == media_id, Media.user_id == user.id)
    )
    media = result.scalar_one_or_none()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    await db.delete(media)