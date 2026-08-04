"""
AI Multi-Agent System API endpoints.

Exposes the Master Agent and individual agents for orchestration.
"""

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.agents.base import AgentContext
from app.agents.master.agent import MasterAgent

router = APIRouter()
master_agent = MasterAgent()


class DemoWorkflowRequest(BaseModel):
    """Request for the public demo workflow — runs any subset of the 9 agents."""
    keyword: str
    niche: str = "general"
    audience: str = ""
    tone: str = "professional"
    goal: str = "engagement"
    agents: list[str] = [
        "trend", "seo", "content", "design", "quality",
        "scheduler", "analytics", "strategy",
    ]


ALL_AGENTS = {
    "trend": {"display": "Trend Agent", "desc": "Trend discovery & opportunities"},
    "seo": {"display": "SEO Agent", "desc": "Keyword research & SEO scoring"},
    "content": {"display": "Content Agent", "desc": "Titles, descriptions, hashtags, CTAs"},
    "design": {"display": "Design Agent", "desc": "Graphic specs & design variations"},
    "quality": {"display": "Quality Agent", "desc": "Quality checks & policy review"},
    "scheduler": {"display": "Scheduler Agent", "desc": "Posting windows & queue"},
    "analytics": {"display": "Analytics Agent", "desc": "Performance metrics & reports"},
    "strategy": {"display": "Strategy Agent", "desc": "Growth recommendations & roadmap"},
}


@router.post("/demo-workflow")
async def run_demo_workflow(body: DemoWorkflowRequest):
    """Public endpoint — runs all (or selected) agents without auth or database.

    Used by the dashboard to demonstrate every agent generating real output.
    Each agent returns its full structured output for proof.
    """
    keyword = body.keyword.strip()
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    ctx = AgentContext(
        workflow_id=str(uuid4()),
        keyword=keyword,
        niche=body.niche or "general",
        audience=body.audience,
        tone=body.tone,
        goal=body.goal,
    )

    # Filter to valid agent names, preserving canonical order
    requested = [a for a in ALL_AGENTS if a in body.agents]
    results = []

    for name in requested:
        agent = master_agent.agents[name]
        res = await agent.run(ctx)
        results.append({
            "name": name,
            "display": ALL_AGENTS[name]["display"],
            "desc": ALL_AGENTS[name]["desc"],
            "success": res.success,
            "processing_time_ms": res.processing_time_ms,
            "output": res.output,
            "suggestions": res.suggestions,
        })

        # Propagate context like the Master Agent does
        if name == "trend" and res.success:
            ctx.trend_data = res.output
        elif name == "seo" and res.success:
            ctx.generated_keywords = res.output.get("keywords", [])
            ctx.seo_score = res.output.get("seo_score", 0.0)
        elif name == "content" and res.success:
            ctx.generated_titles = res.output.get("titles", [])
            ctx.generated_descriptions = res.output.get("descriptions", [])
            ctx.generated_hashtags = res.output.get("hashtags", [])
        elif name == "design" and res.success:
            ctx.generated_images = res.output.get("images", [])
        elif name == "quality" and res.success:
            ctx.quality_score = res.output.get("quality_score", 0.0)

    return {
        "success": True,
        "workflow_id": ctx.workflow_id,
        "keyword": keyword,
        "niche": ctx.niche,
        "agents": results,
        "master": {
            "seo_score": ctx.seo_score,
            "quality_score": ctx.quality_score,
            "total_processing_time_ms": round(sum(r["processing_time_ms"] for r in results), 2),
            "agents_run": len(results),
        },
    }

@router.post("/run-workflow")
async def run_full_workflow(
    keyword: str,
    niche: str = "general",
    audience: str = "",
    tone: str = "professional",
    goal: str = "engagement",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Run the complete multi-agent workflow from trend discovery to strategy."""
    context = AgentContext(
        user_id=str(user.id),
        keyword=keyword,
        niche=niche,
        audience=audience,
        tone=tone,
        goal=goal,
    )
    result = await master_agent.execute(context)
    return {
        "success": result.success,
        "workflow_id": result.workflow_id,
        "output": result.output,
        "processing_time_ms": result.processing_time_ms,
        "error": result.error,
    }


@router.post("/trend-scan")
async def run_trend_scan(
    keyword: str,
    niche: str = "general",
    user: User = Depends(get_current_user),
):
    """Run only the trend discovery agent."""
    result = await master_agent.run_trend_scan(keyword, niche, str(user.id))
    return {
        "success": result.success,
        "output": result.output,
        "suggestions": result.suggestions,
        "processing_time_ms": result.processing_time_ms,
    }


@router.post("/generate-content")
async def run_content_generation(
    keyword: str,
    niche: str = "general",
    tone: str = "professional",
    audience: str = "",
    count: int = 5,
    user: User = Depends(get_current_user),
):
    """Run the SEO + Content generation workflow."""
    result = await master_agent.run_content_generation(
        keyword, niche, tone, audience, count, str(user.id)
    )
    return {
        "success": result.success,
        "output": result.output,
        "processing_time_ms": result.processing_time_ms,
    }


@router.get("/agents")
async def list_agents():
    """List all available agents and their capabilities."""
    return {
        "agents": [
            {"name": "Master", "description": "Coordinates all agents and manages workflows"},
            {"name": "Trend", "description": "Discovers trending topics and content opportunities"},
            {"name": "SEO", "description": "Keyword research, SEO optimization, metadata generation"},
            {"name": "Content", "description": "Generates titles, descriptions, hashtags, and CTAs"},
            {"name": "Design", "description": "Creates Pinterest-optimized images and design variations"},
            {"name": "Quality", "description": "Reviews content quality, grammar, and policy compliance"},
            {"name": "Scheduler", "description": "Optimizes publishing schedules and queue management"},
            {"name": "Analytics", "description": "Analyzes performance data and generates reports"},
            {"name": "Strategy", "description": "Generates strategic recommendations and growth roadmap"},
        ],
        "total_agents": 9,
    }