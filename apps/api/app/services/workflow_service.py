"""
Master Workflow Service — the full AI Content OS pipeline orchestrator.

Runs the complete workflow:
1. Trend Agent researches opportunities
2. SEO Agent builds keyword clusters
3. Content Agent generates article draft
4. Graphic Rendering Engine creates Pinterest graphics
5. Pinterest module generates titles, descriptions, hashtags, boards
6. Everything saved as draft in Website CMS
7. Publishing queue items created (require user approval)
8. Notifications created for review
9. Analytics & revenue tracking enabled

Every stage is observable (writes to AIJobs + Logs) and recovers gracefully.
"""

import json
import uuid as uuid_module
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.trend.agent import TrendAgent
from app.agents.seo.agent import SEOAgent
from app.agents.content.agent import ContentAgent
from app.agents.quality.agent import QualityAgent
from app.agents.scheduler.agent import SchedulerAgent
from app.models.article import Article
from app.models.pin import Pin
from app.models.graphic import Graphic
from app.models.queue import PublishingQueue
from app.models.job import AIJob
from app.models.notification import Notification
from app.models.log import Log
from app.utils import unique_slugify
from app.services.ai_service import get_ai_provider


class WorkflowService:
    """Orchestrates the full content generation pipeline."""

    async def run_full_workflow(self, db: AsyncSession, user_id: str,
                                 topic: str, niche: str = "", audience: str = "",
                                 tone: str = "professional",
                                 brand_color: str = "#2563EB",
                                 affiliate_links: list[str] = None,
                                 internal_links: list[dict] = None,
                                 trusted_sources: list[str] = None,
                                 additional_instructions: str = "") -> dict:
        """Run the complete pipeline from topic to CMS draft + queue items."""
        if affiliate_links is None:
            affiliate_links = []
        if internal_links is None:
            internal_links = []
        if trusted_sources is None:
            trusted_sources = []
        job = self._create_job(db, user_id, "full_workflow", topic, niche)
        await db.flush()

        try:
            stages = {}

            # Stage 1: Trend research
            trend_agent = TrendAgent()
            trend_ctx = await trend_agent.run_trend_scan(topic, niche or "general")
            stages["trend"] = trend_ctx

            # Stage 2: SEO keyword clusters
            seo_agent = SEOAgent()
            seo_ctx = await seo_agent.run_seo_analysis(topic, niche or "general")
            stages["seo"] = seo_ctx
            keywords = seo_ctx.get("keywords", []) if seo_ctx else []

            # Stage 3: Content generation (article draft + Pinterest assets)
            content_agent = ContentAgent()
            content_ctx = await content_agent.run_content_generation(
                topic, niche or "general", tone, audience, count=5
            )
            stages["content"] = content_ctx
            titles = content_ctx.get("titles", []) if content_ctx else []
            descriptions = content_ctx.get("descriptions", []) if content_ctx else []
            hashtags = content_ctx.get("hashtags", []) if content_ctx else []

            # Stage 4: Quality review
            quality_agent = QualityAgent()
            quality_ctx = await quality_agent.run_quality_review(
                topic, titles, descriptions
            )
            stages["quality"] = quality_ctx
            quality_score = quality_ctx.get("quality_score", 80) if quality_ctx else 80

            # Stage 5: Scheduling recommendations
            scheduler_agent = SchedulerAgent()
            schedule_ctx = await scheduler_agent.run_schedule_recommendation(topic)
            stages["scheduler"] = schedule_ctx

            # Stage 6: Save article draft to CMS
            user_uuid = self._coerce_uuid(user_id)

            ai_provider = get_ai_provider()
            generated_data = await ai_provider.generate_article(
                topic=topic,
                affiliate_links=affiliate_links,
                internal_links=internal_links,
                trusted_sources=trusted_sources,
                additional_instructions=additional_instructions,
                tone=tone,
            )
            
            head_title = generated_data.get("title", topic)
            
            from app.utils import slugify
            base_slug = slugify(head_title)
            slug = base_slug
            counter = 2
            
            while True:
                existing = await db.execute(select(Article.id).where(Article.slug == slug))
                if existing.scalar_one_or_none() is None:
                    break
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            html_content = generated_data.get("html", "")
            excerpt = generated_data.get("excerpt", descriptions[0] if descriptions else "")

            article = Article(
                user_id=user_uuid,
                title=head_title,
                slug=slug,
                content=html_content,
                excerpt=excerpt,
                status="draft",
                seo_score=quality_score,
                ai_generated=True,
                ai_metadata=generated_data,
                ai_job_id=job.id,
                category_id=None,
            )
            db.add(article)
            await db.flush()

            # Stage 7: Create Pinterest pin draft
            pin = Pin(
                user_id=article.user_id,
                title=titles[0].get("title", topic) if titles else topic,
                description=descriptions[0] if descriptions else "",
                status="draft",
                is_generated=True,
                seo_score=titles[0].get("seo_score", quality_score) if titles else quality_score,
            )
            db.add(pin)
            await db.flush()

            # Stage 8: Create graphic record (rendering engine metadata)
            graphic = Graphic(
                user_id=article.user_id,
                article_id=article.id,
                pin_id=pin.id,
                template_name=self._select_template(niche),
                variation="A",
                quality_score=quality_score,
                width=1000,
                height=1500,
            )
            db.add(graphic)
            await db.flush()

            # Stage 9: Queue items requiring approval
            article_queue = PublishingQueue(
                user_id=article.user_id,
                article_id=article.id,
                content_type="article",
                status="pending_review",
                requires_approval=True,
            )
            pin_queue = PublishingQueue(
                user_id=article.user_id,
                article_id=article.id,
                pin_id=pin.id,
                graphic_id=graphic.id,
                content_type="pin",
                status="pending_review",
                requires_approval=True,
            )
            db.add(article_queue)
            db.add(pin_queue)
            await db.flush()

            # Stage 10: Notifications for review
            db.add(Notification(
                user_id=article.user_id,
                title="Draft Requires Review",
                message=f"Article '{topic}' is ready for review with {len(titles)} pin variations",
                notification_type="draft_review",
                reference_type="article",
                reference_id=str(article.id),
            ))
            db.add(Notification(
                user_id=article.user_id,
                title="AI Generation Complete",
                message=f"Generated {len(titles)} titles, {len(descriptions)} descriptions, {len(hashtags)} hashtags",
                notification_type="ai_complete",
                reference_type="pin",
                reference_id=str(pin.id),
            ))

            # Stage 11: Audit log
            db.add(Log(
                user_id=article.user_id,
                action="workflow.generate",
                resource_type="article",
                resource_id=str(article.id),
                details=json.dumps({
                    "topic": topic,
                    "niche": niche,
                    "stages_completed": len(stages),
                    "queue_items": 2,
                }),
            ))

            # Complete the job
            job.status = "completed"
            job.progress = 100.0
            job.completed_at = datetime.now(timezone.utc)
            job.output_data = json.dumps({
                "article_id": str(article.id),
                "pin_id": str(pin.id),
                "graphic_id": str(graphic.id),
                "article_queue_id": str(article_queue.id),
                "pin_queue_id": str(pin_queue.id),
                "keywords": keywords[:10],
                "titles": titles,
                "descriptions": descriptions,
                "hashtags": hashtags,
                "quality_score": quality_score,
                "recommended_schedule": schedule_ctx,
            })
            await db.flush()

            return {
                "success": True,
                "job_id": str(job.id),
                "article_id": str(article.id),
                "pin_id": str(pin.id),
                "graphic_id": str(graphic.id),
                "queue_item_ids": [str(article_queue.id), str(pin_queue.id)],
                "stages": list(stages.keys()),
                "quality_score": quality_score,
                "keywords": keywords[:10],
                "titles": titles,
                "descriptions": descriptions,
                "hashtags": hashtags,
                "requires_approval": True,
                "status": "pending_review",
            }

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            await db.flush()
            return {
                "success": False,
                "job_id": str(job.id),
                "error": str(e),
                "status": "failed",
            }

    def _create_job(self, db: AsyncSession, user_id: str, job_type: str,
                     topic: str, niche: str) -> AIJob:
        """Create a background job record for observability."""
        job = AIJob(
            user_id=self._coerce_uuid(user_id),
            job_type=job_type,
            status="running",
            progress=10.0,
            started_at=datetime.now(timezone.utc),
            input_data=json.dumps({"topic": topic, "niche": niche}),
        )
        db.add(job)  # persist so the job appears in GET /workflow/jobs
        return job

    @staticmethod
    def _coerce_uuid(value) -> uuid_module.UUID:
        """Convert a UUID string to a UUID object, preserving the actual user id."""
        if isinstance(value, uuid_module.UUID):
            return value
        return uuid_module.UUID(str(value))

    def _build_article_body(self, topic: str, titles: list, descriptions: list[str],
                            hashtags: list[str], keywords: list[str]) -> str:
        """Build a full AI-generated article body from the pipeline output."""
        head = titles[0].get("title", topic) if titles else topic
        body = [f"<h1>{head}</h1>"]
        if descriptions:
            body.append(f"<p>{descriptions[0]}</p>")

        sections = [
            ("Why This Matters", 1),
            ("Key Strategies", 2),
            ("Pro Tips", 3),
        ]
        for title, idx in sections:
            if idx < len(descriptions):
                body.append(f"<h2>{title}</h2>\n<p>{descriptions[idx]}</p>")

        if keywords:
            body.append("<h2>Related Keywords</h2>\n<ul>" + "".join(
                f"<li>{kw}</li>" for kw in keywords[:8]
            ) + "</ul>")
        if hashtags:
            body.append("<h2>Hashtags</h2>\n<p>" + " ".join(hashtags[:10]) + "</p>")
        body.append("<p><em>Generated with AI — review before publishing.</em></p>")
        return "\n".join(body)

    def _select_template(self, niche: str) -> str:
        """Select a graphic template based on niche."""
        niche = niche.lower()
        template_map = {
            "tech": "technology", "technology": "technology",
            "business": "business", "marketing": "business",
            "food": "recipe", "recipe": "recipe",
            "travel": "travel", "fashion": "fashion",
            "education": "education", "how-to": "education",
            "health": "listicle", "fitness": "listicle",
        }
        for key, template in template_map.items():
            if key in niche:
                return template
        return "modern"


class PublishingPipelineService:
    """Handles the approval-required publishing workflow."""

    @staticmethod
    async def approve(db: AsyncSession, queue_item: PublishingQueue) -> dict:
        """User approves content — moves to queued (not published)."""
        queue_item.status = "approved"
        queue_item.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return {"status": "approved", "id": str(queue_item.id)}

    @staticmethod
    async def reject(db: AsyncSession, queue_item: PublishingQueue) -> dict:
        """User rejects content — returns to draft."""
        queue_item.status = "draft"
        queue_item.updated_at = datetime.now(timezone.utc)
        await db.flush()
        return {"status": "rejected_to_draft", "id": str(queue_item.id)}

    @staticmethod
    async def publish(db: AsyncSession, queue_item: PublishingQueue) -> dict:
        """User explicitly publishes — the only way content goes live."""
        if queue_item.status not in ("approved", "queued"):
            raise ValueError("Content must be approved before publishing")

        queue_item.status = "published"
        queue_item.published_at = datetime.now(timezone.utc)
        queue_item.updated_at = datetime.now(timezone.utc)

        # Update the linked article/pin status
        if queue_item.article_id:
            result = await db.execute(
                select(Article).where(Article.id == queue_item.article_id)
            )
            article = result.scalar_one_or_none()
            if article:
                article.status = "published"
                article.published_at = datetime.now(timezone.utc)

        if queue_item.pin_id:
            result = await db.execute(
                select(Pin).where(Pin.id == queue_item.pin_id)
            )
            pin = result.scalar_one_or_none()
            if pin:
                pin.status = "published"
                pin.published_at = datetime.now(timezone.utc)

        await db.flush()
        return {"status": "published", "id": str(queue_item.id)}