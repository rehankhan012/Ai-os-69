"""
Demo / smoke test: run ALL 9 AI agents on a topic and print their outputs.

Usage:
    cd apps/api
    ../.venv/bin/python tests/test_all_agents_demo.py
"""

import asyncio
import json
import sys

# Ensure the app package is importable when run from apps/api
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.base import AgentContext
from app.agents.trend.agent import TrendAgent
from app.agents.seo.agent import SEOAgent
from app.agents.content.agent import ContentAgent
from app.agents.design.agent import DesignAgent
from app.agents.quality.agent import QualityAgent
from app.agents.scheduler.agent import SchedulerAgent
from app.agents.analytics.agent import AnalyticsAgent
from app.agents.strategy.agent import StrategyAgent
from app.agents.master.agent import MasterAgent

TOPIC = "trending AI model top 10"
NICHE = "technology"
AUDIENCE = "tech enthusiasts"
TONE = "professional"

RESULTS = {}


def heading(title: str):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


def show(key, label, result, highlight_keys=None):
    RESULTS[key] = result
    print(f"\n▶ {label}: success={result.success} "
          f"({result.processing_time_ms}ms)")
    if result.error:
        print(f"  ERROR: {result.error}")
        return
    if result.suggestions:
        print("  💡 Suggestions:")
        for s in result.suggestions[:4]:
            print(f"     • {s}")


async def main():
    heading(f"Running ALL 9 Agents on: '{TOPIC}'")

    # ---------- 1. TREND AGENT ----------
    heading("1️⃣  Trend Agent — discovers trending topics & opportunities")
    trend = TrendAgent()
    result = await trend.run(AgentContext(keyword=TOPIC, niche=NICHE))
    show("trend", "TrendAgent", result)
    if result.success:
        out = result.output
        print(f"  Opportunity score: {out.get('opportunity_score')}/100")
        print(f"  Competition: {out.get('competition_estimate')}")
        print(f"  Suggested priority: {out.get('suggested_priority')}")
        print(f"  Trending topics: {out.get('trending_topics')}")
        print(f"  Evergreen ideas: {out.get('evergreen_ideas')}")
        print(f"  Niche suggestions: {out.get('niche_suggestions')}")

    # ---------- 2. SEO AGENT ----------
    heading("2️⃣  SEO Agent — keyword clusters & SEO scores")
    seo = SEOAgent()
    result = await seo.run(AgentContext(keyword=TOPIC, niche=NICHE))
    show("seo", "SEOAgent", result)
    if result.success:
        out = result.output
        print(f"  SEO score: {out.get('seo_score')}/100")
        print(f"  Keyword difficulty: {out.get('keyword_difficulty')}")
        print(f"  Search intent: {out.get('search_intent')}")
        print(f"  Keywords: {out.get('keywords')}")
        print(f"  Long-tail: {out.get('long_tail_keywords')}")
        print(f"  Title tag: {out.get('metadata', {}).get('title_tag')}")

    # ---------- 3. CONTENT AGENT ----------
    heading("3️⃣  Content Agent — titles, descriptions, hashtags, CTAs")
    content = ContentAgent()
    result = await content.run(AgentContext(keyword=TOPIC, niche=NICHE, tone=TONE, audience=AUDIENCE))
    show("content", "ContentAgent", result)
    if result.success:
        out = result.output
        print("  Titles (with SEO scores):")
        for t in out.get("titles", []):
            print(f"     [{t.get('seo_score')}] {t.get('title')}")
        print("  Descriptions:")
        for d in out.get("descriptions", [])[:3]:
            print(f"     • {d}")
        print(f"  Hashtags: {out.get('hashtags')}")
        print(f"  CTA: {out.get('cta')}")
        print(f"  Recommended board: {out.get('recommended_board')}")

    # ---------- 4. DESIGN AGENT ----------
    heading("4️⃣  Design Agent — graphic design specs & variations")
    design = DesignAgent()
    ctx = AgentContext(keyword=TOPIC, niche=NICHE)
    result = await design.run(ctx)
    show("design", "DesignAgent", result)
    if result.success:
        out = result.output
        print(f"  Style: {out.get('style')}")
        print(f"  Color scheme: {out.get('color_scheme', {}).get('name')}")
        print(f"  Typography: {out.get('typography', {}).get('headline_font')} "
              f"{out.get('typography', {}).get('headline_size_px')}px")
        for v in out.get("variations", []):
            print(f"     - {v.get('name')} (readability {v.get('readability')})")

    # ---------- 5. QUALITY AGENT ----------
    heading("5️⃣  Quality Agent — review & validate content")
    quality = QualityAgent()
    ctx = AgentContext(keyword=TOPIC)
    if RESULTS.get("content"):
        titles = RESULTS["content"].output.get("titles", [])
        ctx.generated_titles = [{"title": t["title"]} for t in titles]
    # Chain Design Agent images (as the real workflow does) so the
    # image-availability critical check passes
    if RESULTS.get("design"):
        ctx.generated_images = RESULTS["design"].output.get("images", [])
    result = await quality.run(ctx)
    show("quality", "QualityAgent", result)
    if result.success:
        out = result.output
        print(f"  Quality score: {out.get('quality_score')}/100")
        print(f"  Passed: {out.get('passed')}/{out.get('total_checks')} checks")
        print(f"  Auto-rejected: {out.get('auto_rejected')}")
        print(f"  Summary: {out.get('summary')}")
        for flag in out.get("flags", []):
            print(f"     ⚠ {flag.get('check')}: {flag.get('details')}")

    # ---------- 6. SCHEDULER AGENT ----------
    heading("6️⃣  Scheduler Agent — publishing schedule & queue")
    scheduler = SchedulerAgent()
    result = await scheduler.run(AgentContext(keyword=TOPIC))
    show("scheduler", "SchedulerAgent", result)
    if result.success:
        out = result.output
        print(f"  Best posting time: {out.get('optimal_posting_time')}")
        print(f"  Board rotation: {out.get('board_rotation')}")
        print(f"  Content mix: {out.get('content_mix')}")
        print(f"  Estimated reach: {out.get('estimated_reach')}")
        for slot in out.get("schedule", [])[:3]:
            print(f"     {slot['day']} {slot['time']} — "
                  f"predicted engagement {slot['predicted_engagement']}")

    # ---------- 7. ANALYTICS AGENT ----------
    heading("7️⃣  Analytics Agent — performance & reports")
    analytics = AnalyticsAgent()
    ctx = AgentContext(keyword=TOPIC)
    result = await analytics.run(ctx)
    show("analytics", "AnalyticsAgent", result)
    if result.success:
        out = result.output
        m = out.get("metrics", {})
        print(f"  CTR: {m.get('ctr')}%  |  Growth: {m.get('growth_rate')}%  |  "
              f"Impressions: {m.get('total_impressions'):,}")
        print(f"  Best posting time: {out.get('best_posting_time')}")
        print(f"  Best image style: {out.get('best_image_style')}")
        print(f"  Top pins: {[p['title'] for p in out.get('top_pins', [])]}")
        w = out.get("weekly_report", {}) or {}
        print(f"  Weekly report: {w.get('period')} — {w.get('clicks')} clicks")

    # ---------- 8. STRATEGY AGENT ----------
    heading("8️⃣  Strategy Agent — recommendations & roadmap")
    strategy = StrategyAgent()
    ctx = AgentContext(keyword=TOPIC, niche=NICHE)
    result = await strategy.run(ctx)
    show("strategy", "StrategyAgent", result)
    if result.success:
        out = result.output
        print("  Recommendations:")
        for r in out.get("recommendations", []):
            print(f"     • [{r.get('priority').upper()}] {r.get('title')}")
        print(f"  New niches: {[n['niche'] for n in out.get('new_niches', [])]}")
        for step in out.get("roadmap", [])[:3]:
            print(f"     Week {step['week']}: {step['action']}")

    # ---------- 9. MASTER AGENT (orchestrates all 8 above) ----------
    heading("9️⃣  Master Agent — orchestrates the full workflow")
    master = MasterAgent()
    ctx = AgentContext(keyword=TOPIC, niche=NICHE, audience=AUDIENCE, tone=TONE)
    result = await master.execute(ctx)
    show("master", "MasterAgent", result)
    if result.success:
        out = result.output
        print(f"  Workflow ID: {out.get('workflow_id')}")
        print(f"  Total processing time: {out.get('total_processing_time_ms')}ms")
        print(f"  Final SEO score: {out.get('seo_score')}/100")
        print(f"  Final quality score: {out.get('quality_score')}/100")
        print("  Pipeline steps:")
        for step in out.get("steps", []):
            status = "✅" if step["success"] else "❌"
            print(f"     {status} {step['agent']:12s} "
                  f"({step['processing_time_ms']}ms)")

    # ---------- SUMMARY ----------
    heading("📊 SUMMARY — all 9 agents")
    all_ok = True
    for key, label in [("trend", "Trend"), ("seo", "SEO"), ("content", "Content"),
                       ("design", "Design"), ("quality", "Quality"),
                       ("scheduler", "Scheduler"), ("analytics", "Analytics"),
                       ("strategy", "Strategy"), ("master", "Master")]:
        r = RESULTS.get(key)
        if r is None:
            print(f"  ⚠ {label:12s} — NOT RUN")
            all_ok = False
        elif r.success:
            print(f"  ✅ {label:12s} — OK ({r.processing_time_ms}ms)")
        else:
            print(f"  ❌ {label:12s} — FAILED: {r.error}")
            all_ok = False

    print("\n" + ("🎉 ALL 9 AGENTS PASSED" if all_ok else "⚠ SOME AGENTS FAILED"))
    return all_ok


if __name__ == "__main__":
    ok = asyncio.run(main())
    sys.exit(0 if ok else 1)