"""
AI Provider Abstraction Layer.

Supports OpenAI GPT, Claude, Gemini with a uniform interface.
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
        """Generate a fully formatted SEO article with affiliate links and structured metadata."""
        prompt = PromptLoader.build_article_prompt(
            topic=topic,
            tone=tone,
            affiliate_links=affiliate_links,
            internal_links=internal_links,
            trusted_sources=trusted_sources,
            additional_instructions=additional_instructions
        )

        response_text = await self.generate_text(prompt)
        
        # Parse JSON
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        response_text = response_text.strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            # Fallback structure if parsing fails
            return {
                "title": topic,
                "slug": topic.lower().replace(" ", "-"),
                "excerpt": "",
                "meta_title": topic,
                "meta_description": "",
                "focus_keyword": topic,
                "tags": [],
                "reading_time": 5,
                "word_count": 0,
                "html": response_text,  # Dump the raw output here
                "faq": [],
                "affiliate_links_used": [],
                "internal_links_used": []
            }


class OpenAIProvider(AIProvider):
    """OpenAI GPT integration."""

    def __init__(self):
        import openai
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
            response_format={"type": "json_object"} if "json" in prompt.lower() else None
        )
        return response.choices[0].message.content or ""

    async def generate_titles(self, keyword: str, niche: str, count: int = 5) -> list[dict]:
        prompt = (
            f"Generate {count} Pinterest pin titles for the keyword '{keyword}' "
            f"in the niche '{niche}'. Return as JSON array with 'title' and 'seo_score' keys."
        )
        # TODO: Parse structured JSON response
        return []

    async def generate_description(self, title: str, keyword: str, tone: str) -> str:
        prompt = f"Write a Pinterest pin description for '{title}' about '{keyword}' in a {tone} tone."
        return await self.generate_text(prompt)


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


class GeminiProvider(AIProvider):
    """Google Gemini integration."""

    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        response = await self.model.generate_content_async(prompt)
        return response.text

    async def generate_titles(self, keyword: str, niche: str, count: int = 5) -> list[dict]:
        return []

    async def generate_description(self, title: str, keyword: str, tone: str) -> str:
        return await self.generate_text(f"Write a Pinterest pin description for '{title}' about '{keyword}' in a {tone} tone.")


def get_ai_provider(provider: str | None = None) -> AIProvider:
    """Factory: return the configured AI provider."""
    provider = provider or "openai"
    providers = {
        "openai": OpenAIProvider,
        "claude": AnthropicProvider,
        "gemini": GeminiProvider,
    }
    cls = providers.get(provider.lower())
    if not cls:
        raise ValueError(f"Unknown AI provider: {provider}. Use: {list(providers.keys())}")
    return cls()