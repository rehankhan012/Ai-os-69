"""
Master Workflow API — the unified content pipeline entry point.

Endpoints:
- POST /workflow/generate — run full pipeline (topic → CMS draft + queue)
- GET  /workflow/jobs — list AI background jobs
- GET  /workflow/jobs/{job_id} — get job status
- POST /workflow/pipeline/{queue_id}/approve — user approval
- POST /workflow/pipeline/{queue_id}/reject — user rejection
- POST /workflow/pipeline/{queue_id}/publish — explicit publish
- GET  /workflow/pipeline — list publishing queue with status
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.core.rate_limit import rate_limit
from app.api.auth import get_current_user
from app.models.user import User
from app.models.job import AIJob
from app.models.queue import PublishingQueue
from app.services.workflow_service import WorkflowService, PublishingPipelineService
from pydantic import BaseModel

router = APIRouter()
workflow_service = WorkflowService()
pipeline_service = PublishingPipelineService()


class InternalLinkRequest(BaseModel):
    title: str
    url: str

class GenerateRequest(BaseModel):
    topic: str
    niche: str = ""
    audience: str = ""
    tone: str = "professional"
    brand_color: str = "#2563EB"
    affiliate_links: list[str] = []
    internal_links: list[InternalLinkRequest] = []
    trusted_sources: list[str] = []
    additional_instructions: str = ""


@router.post("/generate")
async def generate_content(
    body: GenerateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit(limit=10, window_seconds=60)),
):
    """Run the full content pipeline: topic → article draft + pins + queue."""
    if not body.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")

    result = await workflow_service.run_full_workflow(
        db=db,
        user_id=str(user.id),
        topic=body.topic.strip(),
        niche=body.niche,
        audience=body.audience,
        tone=body.tone,
        brand_color=body.brand_color,
        affiliate_links=body.affiliate_links,
        internal_links=[{"title": link.title, "url": link.url} for link in body.internal_links],
        trusted_sources=body.trusted_sources,
        additional_instructions=body.additional_instructions,
    )
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Workflow failed"))
    return result


@router.get("/jobs")
async def list_jobs(
    limit: int = 20,
    status: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List AI background jobs."""
    query = select(AIJob).where(AIJob.user_id == user.id).order_by(desc(AIJob.created_at))
    if status:
        query = query.where(AIJob.status == status)
    query = query.limit(limit)
    result = await db.execute(query)
    jobs = result.scalars().all()
    return [
        {
            "id": str(j.id),
            "job_type": j.job_type,
            "status": j.status,
            "progress": j.progress,
            "error_message": j.error_message,
            "created_at": j.created_at.isoformat(),
            "started_at": j.started_at.isoformat() if j.started_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
        }
        for j in jobs
    ]


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single job's status and output."""
    result = await db.execute(
        select(AIJob).where(AIJob.id == job_id, AIJob.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": str(job.id),
        "job_type": job.job_type,
        "status": job.status,
        "progress": job.progress,
        "error_message": job.error_message,
        "output_data": job.output_data,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


@router.get("/pipeline")
async def list_pipeline(
    status: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List publishing queue items with approval state."""
    query = select(PublishingQueue).where(PublishingQueue.user_id == user.id).order_by(
        desc(PublishingQueue.created_at)
    )
    if status:
        query = query.where(PublishingQueue.status == status)
    result = await db.execute(query)
    items = result.scalars().all()
    return [
        {
            "id": str(q.id),
            "content_type": q.content_type,
            "status": q.status,
            "requires_approval": q.requires_approval,
            "article_id": str(q.article_id) if q.article_id else None,
            "pin_id": str(q.pin_id) if q.pin_id else None,
            "scheduled_at": q.scheduled_at.isoformat() if q.scheduled_at else None,
            "published_at": q.published_at.isoformat() if q.published_at else None,
            "created_at": q.created_at.isoformat(),
        }
        for q in items
    ]


@router.post("/pipeline/{queue_id}/approve")
async def approve_item(
    queue_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approve content for publication (moves to approved, not published)."""
    item = await _get_queue_item(db, user, queue_id)
    return await pipeline_service.approve(db, item)


@router.post("/pipeline/{queue_id}/reject")
async def reject_item(
    queue_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reject content — returns to draft for editing."""
    item = await _get_queue_item(db, user, queue_id)
    return await pipeline_service.reject(db, item)


@router.post("/pipeline/{queue_id}/publish")
async def publish_item(
    queue_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Explicitly publish content — the only path to go live."""
    item = await _get_queue_item(db, user, queue_id)
    try:
        result = await pipeline_service.publish(db, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Create publish notification
    from app.models.notification import Notification
    from datetime import datetime, timezone
    db.add(Notification(
        user_id=user.id,
        title="Content Published",
        message=f"{item.content_type.capitalize()} published successfully",
        notification_type="publish_success",
        reference_type=item.content_type,
        reference_id=str(item.id),
    ))
    return result


async def _get_queue_item(db: AsyncSession, user: User, queue_id: str) -> PublishingQueue:
    """Fetch a queue item owned by the user."""
    result = await db.execute(
        select(PublishingQueue).where(
            PublishingQueue.id == queue_id,
            PublishingQueue.user_id == user.id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Queue item not found")
    return item