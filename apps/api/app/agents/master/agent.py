"""
Master Agent — orchestrates all other agents in a coordinated workflow.

Responsibilities:
- Assign tasks to specialized agents
- Manage workflow state
- Prevent duplicate work
- Log all actions
- Report workflow completion
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.agents.trend.agent import TrendAgent
from app.agents.seo.agent import SEOAgent
from app.agents.content.agent import ContentAgent
from app.agents.design.agent import DesignAgent
from app.agents.quality.agent import QualityAgent
from app.agents.scheduler.agent import SchedulerAgent
from app.agents.analytics.agent import AnalyticsAgent
from app.agents.strategy.agent import StrategyAgent


class MasterAgent(BaseAgent):
    """Coordinates the full content creation workflow across all agents."""

    def __init__(self):
        super().__init__()
        self.name = "Master"
        self.agents = {
            "trend": TrendAgent(),
            "seo": SEOAgent(),
            "content": ContentAgent(),
            "design": DesignAgent(),
            "quality": QualityAgent(),
            "scheduler": SchedulerAgent(),
            "analytics": AnalyticsAgent(),
            "strategy": StrategyAgent(),
        }

    async def execute(self, context: AgentContext) -> AgentResult:
        """Run the full multi-agent workflow in sequence."""
        if not context.workflow_id:
            context.workflow_id = str(uuid4())

        self._log(f"Workflow {context.workflow_id} started", context)
        workflow_steps = []

        # Step 1: Trend Discovery
        trend_result = await self.agents["trend"].run(context)
        workflow_steps.append(("trend", trend_result))
        if trend_result.success and trend_result.output:
            context.trend_data = trend_result.output

        # Step 2: SEO Analysis
        seo_result = await self.agents["seo"].run(context)
        workflow_steps.append(("seo", seo_result))
        if seo_result.success:
            context.generated_keywords = seo_result.output.get("keywords", context.generated_keywords)
            context.seo_score = seo_result.output.get("seo_score", 0.0)

        # Step 3: Content Generation
        content_result = await self.agents["content"].run(context)
        workflow_steps.append(("content", content_result))
        if content_result.success:
            context.generated_titles = content_result.output.get("titles", context.generated_titles)
            context.generated_descriptions = content_result.output.get("descriptions", context.generated_descriptions)
            context.generated_hashtags = content_result.output.get("hashtags", context.generated_hashtags)

        # Step 4: Design / Image Generation
        design_result = await self.agents["design"].run(context)
        workflow_steps.append(("design", design_result))
        if design_result.success:
            context.generated_images = design_result.output.get("images", context.generated_images)

        # Step 5: Quality Review
        quality_result = await self.agents["quality"].run(context)
        workflow_steps.append(("quality", quality_result))
        if quality_result.success:
            context.quality_score = quality_result.output.get("quality_score", 0.0)
            context.quality_flags = quality_result.output.get("flags", [])

        # Step 6: Scheduling
        schedule_result = await self.agents["scheduler"].run(context)
        workflow_steps.append(("scheduler", schedule_result))

        # Step 7: Analytics (historical)
        analytics_result = await self.agents["analytics"].run(context)
        workflow_steps.append(("analytics", analytics_result))

        # Step 8: Strategy Recommendations
        strategy_result = await self.agents["strategy"].run(context)
        workflow_steps.append(("strategy", strategy_result))
        if strategy_result.success:
            context.strategy_recommendations = strategy_result.output.get("recommendations", [])

        # Compile results
        summary = self._compile_summary(workflow_steps, context)
        self._log(f"Workflow {context.workflow_id} completed", context)

        return AgentResult(
            success=True,
            agent_name=self.name,
            workflow_id=context.workflow_id,
            output={
                "workflow_id": context.workflow_id,
                "steps": summary,
                "context": context.model_dump(),
                "quality_score": context.quality_score,
                "seo_score": context.seo_score,
                "total_processing_time_ms": sum(s["processing_time_ms"] for s in summary),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    def _compile_summary(self, steps: list[tuple[str, AgentResult]], context: AgentContext) -> list[dict]:
        """Compile a readable summary of all workflow steps."""
        return [
            {
                "agent": name,
                "success": result.success,
                "error": result.error,
                "processing_time_ms": result.processing_time_ms,
            }
            for name, result in steps
        ]

    async def run_trend_scan(self, keyword: str, niche: str, user_id: str = "") -> AgentResult:
        """Run only the trend discovery workflow (lightweight)."""
        ctx = AgentContext(keyword=keyword, niche=niche, user_id=user_id)
        ctx.workflow_id = str(uuid4())
        return await self.agents["trend"].run(ctx)

    async def run_content_generation(self, keyword: str, niche: str, tone: str = "professional",
                                      audience: str = "", count: int = 5, user_id: str = "") -> AgentResult:
        """Run SEO + Content generation workflow."""
        ctx = AgentContext(keyword=keyword, niche=niche, tone=tone, audience=audience, user_id=user_id)
        ctx.workflow_id = str(uuid4())

        seo_result = await self.agents["seo"].run(ctx)
        if seo_result.success:
            ctx.generated_keywords = seo_result.output.get("keywords", [])

        content_result = await self.agents["content"].run(ctx)
        quality_result = await self.agents["quality"].run(ctx)

        return AgentResult(
            success=content_result.success and quality_result.success,
            agent_name=self.name,
            workflow_id=ctx.workflow_id,
            output={
                "titles": ctx.generated_titles,
                "descriptions": ctx.generated_descriptions,
                "hashtags": ctx.generated_hashtags,
                "keywords": ctx.generated_keywords,
                "seo_score": ctx.seo_score,
                "quality_score": ctx.quality_score,
            },
        )