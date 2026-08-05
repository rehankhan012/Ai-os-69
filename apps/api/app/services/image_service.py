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
    provider = provider or "flux"
    providers = {
        "flux": FLUXProvider,
        "ideogram": IdeogramProvider,
    }
    cls = providers.get(provider.lower())
    if not cls:
        raise ValueError(f"Unknown image provider: {provider}. Use: {list(providers.keys())}")
    return cls()