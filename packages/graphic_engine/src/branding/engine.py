"""
Branding Engine — manages brand profiles, logo placement, and footer overlays.

Supports:
- Logo placement (URL or text-based)
- Website URL
- Social handle
- Brand colors
- Custom fonts
- Footer with watermark
- Reusable brand profiles
"""

from dataclasses import dataclass, field
from typing import Optional

from packages.graphic_engine.src.engine.spec import DesignSpec


@dataclass
class BrandProfile:
    """A reusable brand profile."""
    name: str = "Default"
    primary_color: str = "#E94560"
    secondary_color: str = "#1A1A2E"
    accent_color: str = "#0F3460"
    background_color: str = "#FFFFFF"
    text_color: str = "#1A1A2E"
    headline_font: str = "Inter"
    body_font: str = "Inter"
    logo_url: Optional[str] = None
    logo_text: str = ""
    website: str = ""
    social_handle: str = ""
    footer_text: str = "Follow for more"
    show_logo: bool = True
    show_footer: bool = True
    watermark_opacity: float = 0.3


class BrandingEngine:
    """Handles branding overlay on rendered graphics."""

    DEFAULT_PROFILES: dict[str, BrandProfile] = {
        "default": BrandProfile(
            name="Default",
            primary_color="#E94560",
            secondary_color="#1A1A2E",
            accent_color="#0F3460",
            footer_text="Follow for more content",
        ),
        "premium": BrandProfile(
            name="Premium",
            primary_color="#D4AF37",
            secondary_color="#1A1A2E",
            accent_color="#8B7530",
            background_color="#FFFFFF",
            text_color="#1A1A2E",
            headline_font="Playfair Display",
            body_font="Inter",
            footer_text="Follow for exclusive content",
        ),
        "tech": BrandProfile(
            name="Tech",
            primary_color="#2563EB",
            secondary_color="#0F172A",
            accent_color="#3B82F6",
            background_color="#0F172A",
            text_color="#FFFFFF",
            headline_font="Space Grotesk",
            body_font="Inter",
            footer_text="Follow for tech insights",
        ),
        "minimal": BrandProfile(
            name="Minimal",
            primary_color="#1A1A2E",
            secondary_color="#333333",
            accent_color="#666666",
            background_color="#FFFFFF",
            text_color="#1A1A2E",
            headline_font="Inter",
            body_font="Inter",
            footer_text="Follow for more",
        ),
    }

    @classmethod
    def get_profile(cls, name: str = "default") -> BrandProfile:
        """Get a brand profile by name."""
        return cls.DEFAULT_PROFILES.get(name, cls.DEFAULT_PROFILES["default"])

    @classmethod
    def create_profile(cls, name: str, **kwargs) -> BrandProfile:
        """Create a new brand profile."""
        profile = BrandProfile(name=name, **kwargs)
        cls.DEFAULT_PROFILES[name] = profile
        return profile

    @staticmethod
    def generate_branding_overlay(spec: DesignSpec) -> str:
        """Generate SVG branding overlay markup."""
        markup = ""
        w, h = spec.layout.width, spec.layout.height
        branding = spec.branding
        colors = spec.colors

        if not branding.show_footer:
            return markup

        # Footer bar
        markup += (
            f'<rect x="0" y="{h-70}" width="{w}" height="70" '
            f'fill="{colors.secondary}" opacity="0.03"/>'
        )

        # Social handle
        if branding.social_handle:
            markup += (
                f'<text x="{w//2}" y="{h-35}" text-anchor="middle" '
                f'font-family="Inter" font-size="13" font-weight="600" '
                f'fill="{colors.text_light}" opacity="0.7">'
                f'{branding.social_handle}</text>'
            )
        elif branding.footer_text:
            markup += (
                f'<text x="{w//2}" y="{h-35}" text-anchor="middle" '
                f'font-family="Inter" font-size="13" font-weight="500" '
                f'fill="{colors.text_light}" opacity="0.6">'
                f'{branding.footer_text}</text>'
            )

        # Website URL
        if branding.website:
            markup += (
                f'<text x="{w//2}" y="{h-48}" text-anchor="middle" '
                f'font-family="Inter" font-size="11" font-weight="400" '
                f'fill="{colors.text_light}" opacity="0.4">'
                f'{branding.website}</text>'
            )

        # Logo text (top-left)
        if branding.show_footer and branding.logo_url is None:
            markup += (
                f'<text x="40" y="40" font-family="Inter" font-size="11" '
                f'font-weight="700" fill="{colors.primary}" opacity="0.5" '
                f'letter-spacing="2">'
                f'{branding.footer_text[:3].upper()}</text>'
            )

        # Bottom accent line
        markup += (
            f'<rect x="{w//2-30}" y="{h-70}" width="60" height="2" '
            f'rx="1" fill="{colors.primary}" opacity="0.3"/>'
        )

        return markup

    @staticmethod
    def apply_brand_profile(spec: DesignSpec, profile: BrandProfile) -> DesignSpec:
        """Apply a brand profile to an existing design spec."""
        spec.colors.primary = profile.primary_color
        spec.colors.secondary = profile.secondary_color
        spec.colors.accent = profile.accent_color
        spec.colors.background = profile.background_color
        spec.colors.text = profile.text_color
        spec.typography.headline_font = profile.headline_font
        spec.typography.body_font = profile.body_font
        spec.branding.footer_text = profile.footer_text
        spec.branding.logo_url = profile.logo_url
        spec.branding.social_handle = profile.social_handle
        spec.branding.website = profile.website
        return spec