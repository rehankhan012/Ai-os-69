"""
Image Generation Provider Abstraction.

Supports GPT Image, FLUX, Ideogram, and future providers.
"""

from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings


class ImageProvider(ABC):
    """Abstract base class for image generation providers."""

    @abstractmethod
    async def generate_image(self, prompt: str, style: str, width: int = 1000, height: int = 1500) -> bytes:
        ...


class OpenAIImageProvider(ImageProvider):
    """OpenAI DALL-E integration."""

    def __init__(self):
        import openai
        self.client = openai.AsyncOpenAI(api_key=settings.openai_image_api_key or settings.openai_api_key)

    async def generate_image(self, prompt: str, style: str, width: int = 1000, height: int = 1500) -> bytes:
        response = await self.client.images.generate(
            model="dall-e-3",
            prompt=f"{prompt} — Pinterest vertical pin, {style} style, 1000x1500, readable typography, balanced layout",
            size="1024x1792",
            quality="standard",
            n=1,
        )
        # Download image bytes from URL
        import httpx
        async with httpx.AsyncClient() as client:
            img_response = await client.get(response.data[0].url)
            return img_response.content


class FLUXProvider(ImageProvider):
    """FLUX image generation integration."""

    async def generate_image(self, prompt: str, style: str, width: int = 1000, height: int = 1500) -> bytes:
        # TODO: Implement FLUX API integration
        raise NotImplementedError("FLUX provider not yet implemented")


class IdeogramProvider(ImageProvider):
    """Ideogram image generation integration."""

    async def generate_image(self, prompt: str, style: str, width: int = 1000, height: int = 1500) -> bytes:
        # TODO: Implement Ideogram API integration
        raise NotImplementedError("Ideogram provider not yet implemented")


def get_image_provider(provider: str | None = None) -> ImageProvider:
    """Factory: return the configured image provider."""
    provider = provider or "openai"
    providers = {
        "openai": OpenAIImageProvider,
        "flux": FLUXProvider,
        "ideogram": IdeogramProvider,
    }
    cls = providers.get(provider.lower())
    if not cls:
        raise ValueError(f"Unknown image provider: {provider}. Use: {list(providers.keys())}")
    return cls()