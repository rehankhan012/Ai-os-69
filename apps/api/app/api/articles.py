"""
Website CMS — Article CRUD + publish endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.config import settings
from app.api.auth import get_current_user
from app.models.user import User
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag
from app.models.queue import PublishingQueue
from app.models.pin import Pin
from app.models.graphic import Graphic
from app.models.notification import Notification
from app.services.website_publisher import website_publisher, WebsitePublisherError
from app.utils import slugify
from pydantic import BaseModel

router = APIRouter()


class ArticleCreate(BaseModel):
    title: str
    content: str | None = None
    excerpt: str | None = None
    category_id: str | None = None
    status: str = "draft"


class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    excerpt: str | None = None
    featured_image_url: str | None = None
    category_id: str | None = None
    status: str | None = None


@router.get("/")
async def list_articles(
    status: str | None = None,
    category_id: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List articles with filters."""
    query = select(Article).where(Article.user_id == user.id).order_by(Article.updated_at.desc())

    if status:
        query = query.where(Article.status == status)
    if category_id:
        query = query.where(Article.category_id == category_id)
    if search:
        query = query.where(Article.title.ilike(f"%{search}%"))

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    articles = result.scalars().all()
    return [
        {
            "id": str(a.id),
            "title": a.title,
            "slug": a.slug,
            "excerpt": a.excerpt,
            "status": a.status,
            "seo_score": a.seo_score,
            "ai_generated": a.ai_generated,
            "view_count": a.view_count,
            "published_at": a.published_at.isoformat() if a.published_at else None,
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat(),
        }
        for a in articles
    ]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_article(
    body: ArticleCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new article."""
    # Ensure a unique, URL-safe slug for the public site
    import uuid as uuid_module

    existing = set((await db.execute(select(Article.slug))).scalars().all())
    slug = slugify(body.title, 80)
    if slug in existing:
        slug = f"{slug}-{uuid_module.uuid4().hex[:6]}"
    article = Article(
        user_id=user.id,
        title=body.title,
        slug=slug,
        content=body.content,
        excerpt=body.excerpt,
        category_id=body.category_id,
        status=body.status,
    )
    db.add(article)
    await db.flush()
    await db.refresh(article)

    # Update category count
    if body.category_id:
        cat = await db.execute(select(Category).where(Category.id == body.category_id))
        cat_obj = cat.scalar_one_or_none()
        if cat_obj:
            cat_obj.article_count += 1

    return {
        "id": str(article.id),
        "title": article.title,
        "status": article.status,
        "created_at": article.created_at.isoformat(),
    }


@router.post("/{article_id}/publish")
async def publish_article(
    article_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Full publish: mark published in the CMS, push to the website (if configured),
    upload the related pin to Pinterest (if connected), and create a notification.
    Returns a per-step report so the dashboard can show exactly what happened.
    """
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.user_id == user.id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    report: dict = {"article_id": str(article.id)}

    # ---- 1. Local CMS publish ----
    article.status = "published"
    if not article.published_at:
        article.published_at = datetime.now(timezone.utc)
    report["cms"] = {"status": "published", "message": "Article is live in your CMS."}

    # ---- 2. Website publish (pluggable) ----
    try:
        report["website"] = await website_publisher.publish_article(article)
    except WebsitePublisherError as e:
        report["website"] = {"status": "error", "message": str(e)}

    # ---- 3. Pinterest pin publish (graceful when not connected) ----
    pin_id = await _pin_id_for_article(db, user, article)
    if not pin_id:
        report["pinterest"] = {
            "status": "skipped",
            "message": "No pin was generated for this article — run the pipeline with pin generation enabled.",
        }
    elif not (settings.pinterest_client_id and settings.pinterest_client_secret):
        report["pinterest"] = {
            "status": "skipped",
            "message": "Pinterest not connected — add PINTEREST_CLIENT_ID / PINTEREST_CLIENT_SECRET in the API .env and reconnect in Settings.",
        }
    else:
        try:
            pin = (await db.execute(select(Pin).where(Pin.id == pin_id, Pin.user_id == user.id))).scalar_one_or_none()
            if not pin:
                raise HTTPException(status_code=404, detail="Pin not found")

            # Resolve an image: graphic png_path or svg -> rasterize, else report cleanly
            from app.api.pinterest import _rasterize_svg

            image_bytes = None
            graphic = None
            gres = await db.execute(select(Graphic).where(Graphic.pin_id == pin.id))
            graphic = gres.scalar_one_or_none()
            if graphic and graphic.png_path:
                image_bytes = open(graphic.png_path, "rb").read()
            elif graphic and graphic.svg_content:
                image_bytes = _rasterize_svg(graphic.svg_content, graphic.width or 1000, graphic.height or 1500)

            if image_bytes is None:
                report["pinterest"] = {
                    "status": "skipped",
                    "message": "Pin image not available — create a graphic in the Graphic Studio, then publish again.",
                }
            else:
                from app.services.pinterest_service import pinterest_service
                from packages.pinterest import PinterestAuthError, PinterestAPIError

                try:
                    remote = await pinterest_service.publish_pin(
                        db=db, user=user, board_id=pin.board_id or "",
                        title=pin.title, description=pin.description or "",
                        image_bytes=image_bytes,
                    )
                    pin.status = "published"
                    pin.published_at = datetime.now(timezone.utc)
                    report["pinterest"] = {
                        "status": "published",
                        "pin_id": remote.get("id", str(pin.id)),
                        "url": remote.get("url", ""),
                        "message": "Pin uploaded to Pinterest.",
                    }
                except PinterestAuthError as e:
                    report["pinterest"] = {"status": "error", "message": str(e)}
                except PinterestAPIError as e:
                    report["pinterest"] = {"status": "error", "message": str(e)}
        except Exception as e:  # defensive — never break the whole publish on pin issues
            report["pinterest"] = {"status": "error", "message": str(e)}

    # ---- 4. Sync related publishing-queue items ----
    qres = await db.execute(
        select(PublishingQueue).where(PublishingQueue.article_id == article.id)
    )
    for q in qres.scalars().all():
        q.status = "published"
        q.published_at = datetime.now(timezone.utc)

    # ---- 5. Notification ----
    db.add(Notification(
        user_id=user.id,
        title="Content Published",
        message=f"'{article.title}' was published"
        + (" and uploaded to your website" if report.get("website", {}).get("status") == "published" else "")
        + (" and Pinterest" if report.get("pinterest", {}).get("status") == "published" else ""),
        notification_type="publish_success",
        reference_type="article",
        reference_id=str(article.id),
    ))
    await db.flush()

    report["article"] = {"id": str(article.id), "status": "published"}
    return report


async def _pin_id_for_article(db: AsyncSession, user: User, article: Article) -> str | None:
    """Find the pin generated for this article (via the publishing queue link)."""
    qres = await db.execute(
        select(PublishingQueue).where(
            PublishingQueue.article_id == article.id,
            PublishingQueue.pin_id.isnot(None),
        )
    )
    q = qres.scalars().first()
    if q and q.pin_id:
        return str(q.pin_id)
    # Fallback: any pin with the same title
    pres = await db.execute(
        select(Pin).where(Pin.user_id == user.id, Pin.title == article.title).limit(1)
    )
    pin = pres.scalars().first()
    return str(pin.id) if pin else None


@router.get("/{article_id}")
async def get_article(
    article_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single article."""
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.user_id == user.id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {
        "id": str(article.id),
        "title": article.title,
        "content": article.content,
        "excerpt": article.excerpt,
        "slug": article.slug,
        "status": article.status,
        "seo_score": article.seo_score,
        "ai_generated": article.ai_generated,
        "view_count": article.view_count,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat(),
    }


@router.patch("/{article_id}")
async def update_article(
    article_id: str,
    body: ArticleUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an article."""
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.user_id == user.id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(article, key, value)

    if body.status == "published" and not article.published_at:
        article.published_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(article)
    return {"status": "updated", "id": str(article.id)}


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an article."""
    result = await db.execute(
        select(Article).where(Article.id == article_id, Article.user_id == user.id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    await db.delete(article)


from datetime import datetime, timezone