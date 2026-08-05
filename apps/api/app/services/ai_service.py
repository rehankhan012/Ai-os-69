"""
AI Provider Abstraction Layer.

Supports Claude, Gemini with a uniform interface.
"""

from abc import ABC, abstractmethod
from typing import Any

import json
from app.core.config import settings
from app.prompts.prompt_loader import PromptLoader


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        ...

    @abstractmethod
    async def generate_titles(self, keyword: str, niche: str, count: int = 5) -> list[dict]:
        ...

    @abstractmethod
    async def generate_description(self, title: str, keyword: str, tone: str) -> str:
        ...

    async def generate_article(self, topic: str, affiliate_links: list[str], internal_links: list[dict], trusted_sources: list[str], additional_instructions: str, tone: str) -> dict:
        """Generate a fully formatted SEO article with affiliate links and structured metadata using the V3.0 pipeline."""
        from app.services.article_pipeline import ArticlePipelineService
        
        pipeline = ArticlePipelineService(provider=self)
        return await pipeline.run_pipeline(
            topic=topic,
            tone=tone,
            affiliate_links=affiliate_links,
            internal_links=internal_links,
            trusted_sources=trusted_sources,
            additional_instructions=additional_instructions
        )



import json

class MockProvider(AIProvider):
    """Mock AI integration for local testing without API keys."""

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        if "You MUST return your entire response as a structured JSON object matching this schema exactly" in prompt:
            return json.dumps({
                "title": "Mock Article Title",
                "slug": "mock-article-title",
                "meta_title": "Mock Meta Title",
                "meta_description": "Mock Meta Description",
                "excerpt": "Mock summary",
                "focus_keyword": "mock keyword",
                "secondary_keywords": ["mock", "keywords"],
                "tags": ["mock", "test"],
                "reading_time": "5 min read",
                "word_count": 500,
                "seo_score": 98,
                "quality_score": 96,
                "featured_image_prompt": "A mock image prompt",
                "pinterest_prompt": "Mock pin prompt",
                "thumbnail_prompt": "Mock thumbnail",
                "twitter_banner_prompt": "Mock banner",
                "linkedin_cover_prompt": "Mock cover",
                "faq": [{"question": "What is this?", "answer": "A mock article."}],
                "schema": {"article": {}, "faq": {}, "breadcrumb": {}},
                "affiliate_links_used": [],
                "internal_links_used": [],
                "seo_audit": {
                    "keyword_coverage": "Good",
                    "heading_quality": "Good",
                    "internal_links_count": 0,
                    "affiliate_links_count": 0,
                    "external_links_count": 0,
                    "missing_opportunities": [],
                    "improvement_suggestions": []
                },
                "quality_audit": {
                    "helpfulness": 95,
                    "trustworthiness": 95,
                    "depth": 95,
                    "originality": 95,
                    "engagement": 95,
                    "conversion_potential": 95,
                    "human_likeness": 95
                },
                "content_suggestions": {
                    "better_titles": [],
                    "better_meta_descriptions": [],
                    "additional_faqs": [],
                    "suggested_related_articles": [],
                    "suggested_internal_links": [],
                    "content_expansion_ideas": []
                }
            })
        elif "You are an expert HTML Developer" in prompt:
            return "<h1>Mock HTML</h1><p>This is a mock draft converted to HTML.</p>"
        else:
            return "This is a mock response from the AI."

    async def generate_titles(self, keyword: str, niche: str, count: int = 5) -> list[dict]:
        return [{"title": f"Mock Title {i}", "seo_score": 90} for i in range(count)]

    async def generate_description(self, title: str, keyword: str, tone: str) -> str:
        return f"Mock description for {title}"


def get_ai_provider(provider: str | None = None) -> AIProvider:
    """Factory: return the configured AI provider."""
    provider = provider or "mock"
    providers = {
        "mock": MockProvider,
        "claude": MockProvider, # Fallback mapping if old string is used
    }
    cls = providers.get(provider.lower())
    if not cls:
        raise ValueError(f"Unknown AI provider: {provider}. Use: {list(providers.keys())}")
    return cls()