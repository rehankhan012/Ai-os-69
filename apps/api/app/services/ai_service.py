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



class AnthropicProvider(AIProvider):
    """Anthropic Claude integration."""

    def __init__(self):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        response = await self.client.messages.create(
            model=kwargs.get("model", "claude-3-5-sonnet-20241022"),
            max_tokens=kwargs.get("max_tokens", 1024),
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text if response.content else ""

    async def generate_titles(self, keyword: str, niche: str, count: int = 5) -> list[dict]:
        return []

    async def generate_description(self, title: str, keyword: str, tone: str) -> str:
        return await self.generate_text(f"Write a Pinterest pin description for '{title}' about '{keyword}' in a {tone} tone.")


def get_ai_provider(provider: str | None = None) -> AIProvider:
    """Factory: return the configured AI provider."""
    provider = provider or "claude"
    providers = {
        "claude": AnthropicProvider,
    }
    cls = providers.get(provider.lower())
    if not cls:
        raise ValueError(f"Unknown AI provider: {provider}. Use: {list(providers.keys())}")
    return cls()