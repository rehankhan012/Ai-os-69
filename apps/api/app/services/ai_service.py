"""
AI Provider Abstraction Layer.

Exclusively uses Groq as the AI provider.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any
from fastapi import HTTPException

from groq import AsyncGroq
from app.core.config import settings
from app.prompts.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)

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

DEFAULT_MODEL = "llama-3.3-70b-versatile"

class GroqProvider(AIProvider):
    """Groq AI Integration."""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY") or settings.groq_api_key
        if not api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY missing.")
        
        self.client = AsyncGroq(api_key=api_key)
        self.model = DEFAULT_MODEL

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=kwargs.get("temperature", 0.7),
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API Error: {e}")
            raise HTTPException(status_code=500, detail=f"AI Generation Failed: {str(e)}")

    async def generate_titles(self, keyword: str, niche: str, count: int = 5) -> list[dict]:
        prompt = f"Generate {count} highly engaging, SEO-optimized blog titles for the keyword '{keyword}' in the '{niche}' niche. Return ONLY a valid JSON array of objects, each containing 'title' and 'seo_score' (1-100). Do not include markdown blocks or any other text."
        response = await self.generate_text(prompt, temperature=0.8)
        try:
            # Clean possible markdown block
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            return json.loads(response.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse titles JSON: {response}")
            return [{"title": f"{keyword} - The Ultimate Guide", "seo_score": 90}]

    async def generate_description(self, title: str, keyword: str, tone: str) -> str:
        prompt = f"Write a compelling 2-3 sentence meta description for an article titled '{title}' using the keyword '{keyword}'. The tone should be {tone}. Return ONLY the description without quotes or extra text."
        response = await self.generate_text(prompt, temperature=0.7)
        return response.strip(' "')


def get_ai_provider(provider: str | None = None) -> AIProvider:
    """Factory: returns the Groq AI provider exclusively."""
    return GroqProvider()