"""
Shape Engine — generates decorative SVG shapes.

Supports:
- Circles, squares, rounded rectangles
- Lines, borders, dividers
- Blobs (organic shapes)
- Triangles, hexagons
- Frames, accent borders
- Glow effects
- Layered cards
- Number badges (for listicles)
"""

import math
import random
from typing import Optional

from packages.graphic_engine.src.engine.spec import DesignSpec, ShapeSpec


class ShapeEngine:
    """Generates decorative SVG shapes for Pinterest pins."""

    @staticmethod
    def generate_shapes(spec: DesignSpec) -> str:
        """Generate all decorative shapes for the design."""
        markup = ""
        w, h = spec.layout.width, spec.layout.height
        colors = spec.colors
        template = spec.template_name

        # Add shapes based on template
        if template in ("minimal", "modern", "business"):
            markup += ShapeEngine._accent_corner(w, h, colors)
        elif template in ("luxury", "fashion"):
            markup += ShapeEngine._gold_accents(w, h, colors)
        elif template in ("technology", "infographic"):
            markup += ShapeEngine._tech_shapes(w, h, colors)
        elif template in ("travel", "lifestyle"):
            markup += ShapeEngine._organic_shapes(w, h, colors)
        elif template in ("quotes", "motivation"):
            markup += ShapeEngine._quote_decorations(w, h, colors)
        elif template in ("recipe", "food"):
            markup += ShapeEngine._recipe_shapes(w, h, colors)
        elif template in ("education", "listicle"):
            markup += ShapeEngine._list_shapes(w, h, colors)
        elif template in ("glassmorphism",):
            markup += ShapeEngine._glass_shapes(w, h, colors)
        elif template in ("hero", "split"):
            markup += ShapeEngine._hero_shapes(w, h, colors)

        # Add custom shapes from spec
        for shape in spec.shapes.shapes:
            markup += ShapeEngine._render_shape(shape, w, h)

        # Add bottom accent bar
        markup += ShapeEngine._bottom_bar(w, h, colors, template)

        return markup

    @staticmethod
    def _render_shape(shape: dict, w: int, h: int) -> str:
        """Render a single shape from spec."""
        stype = shape.get("type", "circle")
        x = shape.get("x", w // 2)
        y = shape.get("y", h // 2)
        color = shape.get("color", "#eee")
        opacity = shape.get("opacity", 0.3)

        if stype == "circle":
            r = shape.get("radius", 50)
            return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" opacity="{opacity}"/>'
        elif stype == "rect":
            rw = shape.get("width", 100)
            rh = shape.get("height", 100)
            rx = shape.get("border_radius", 0)
            return f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" rx="{rx}" fill="{color}" opacity="{opacity}"/>'
        elif stype == "line":
            x2 = shape.get("x2", x + 100)
            y2 = shape.get("y2", y)
            stroke = shape.get("stroke_width", 2)
            return f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{stroke}" opacity="{opacity}"/>'
        return ""

    @staticmethod
    def _accent_corner(w: int, h: int, colors: any) -> str:
        """Small accent shapes in corners."""
        return (
            f'<circle cx="80" cy="80" r="120" fill="{colors.primary}" opacity="0.06"/>'
            f'<circle cx="{w-80}" cy="{h-80}" r="80" fill="{colors.accent}" opacity="0.04"/>'
            f'<rect x="60" y="{h-120}" width="40" height="4" rx="2" fill="{colors.primary}" opacity="0.3"/>'
        )

    @staticmethod
    def _gold_accents(w: int, h: int, colors: any) -> str:
        """Luxury gold/line accents."""
        gold = "#D4AF37"
        return (
            f'<line x1="80" y1="120" x2="200" y2="120" stroke="{gold}" stroke-width="2" opacity="0.5"/>'
            f'<line x1="{w-80}" y1="{h-120}" x2="{w-200}" y2="{h-120}" stroke="{gold}" stroke-width="2" opacity="0.5"/>'
            f'<rect x="80" y="130" width="60" height="60" rx="30" fill="none" stroke="{gold}" stroke-width="1" opacity="0.2"/>'
            f'<rect x="{w-140}" y="{h-190}" width="60" height="60" rx="30" fill="none" stroke="{gold}" stroke-width="1" opacity="0.2"/>'
        )

    @staticmethod
    def _tech_shapes(w: int, h: int, colors: any) -> str:
        """Tech-themed geometric shapes."""
        return (
            f'<rect x="40" y="40" width="80" height="80" rx="12" fill="{colors.primary}" opacity="0.05"/>'
            f'<rect x="{w-120}" y="40" width="80" height="80" rx="12" fill="{colors.accent}" opacity="0.05"/>'
            f'<circle cx="{w//2}" cy="{h-100}" r="60" fill="none" stroke="{colors.primary}" stroke-width="1" opacity="0.1"/>'
            f'<line x1="100" y1="{h//2}" x2="300" y2="{h//2}" stroke="{colors.primary}" stroke-width="1" opacity="0.08" stroke-dasharray="8,8"/>'
            f'<line x1="{w-100}" y1="{h//2}" x2="{w-300}" y2="{h//2}" stroke="{colors.accent}" stroke-width="1" opacity="0.08" stroke-dasharray="8,8"/>'
        )

    @staticmethod
    def _organic_shapes(w: int, h: int, colors: any) -> str:
        """Organic flowing shapes for lifestyle/travel."""
        return (
            f'<path d="M0 {h*0.85} Q{w*0.3} {h*0.8} {w*0.5} {h*0.88} T{w} {h*0.82} L{w} {h} L0 {h}Z" fill="{colors.primary}" opacity="0.05"/>'
            f'<circle cx="{w*0.15}" cy="{h*0.2}" r="40" fill="{colors.primary}" opacity="0.08"/>'
            f'<circle cx="{w*0.85}" cy="{h*0.75}" r="30" fill="{colors.accent}" opacity="0.06"/>'
        )

    @staticmethod
    def _quote_decorations(w: int, h: int, colors: any) -> str:
        """Quote mark decorations."""
        return (
            f'<text x="80" y="180" font-size="100" font-family="Georgia, serif" fill="{colors.primary}" opacity="0.15">"</text>'
            f'<line x1="80" y1="200" x2="200" y2="200" stroke="{colors.primary}" stroke-width="3" opacity="0.3" stroke-linecap="round"/>'
            f'<line x1="80" y1="208" x2="160" y2="208" stroke="{colors.primary}" stroke-width="2" opacity="0.2" stroke-linecap="round"/>'
        )

    @staticmethod
    def _recipe_shapes(w: int, h: int, colors: any) -> str:
        """Recipe/food decorative shapes."""
        return (
            f'<circle cx="{w*0.5}" cy="{h*0.3}" r="{w*0.35}" fill="{colors.primary}" opacity="0.04"/>'
            f'<circle cx="{w*0.5}" cy="{h*0.3}" r="{w*0.25}" fill="{colors.accent}" opacity="0.03"/>'
            f'<rect x="60" y="{h-200}" width="{w-120}" height="4" rx="2" fill="{colors.primary}" opacity="0.15"/>'
            f'<rect x="60" y="{h-190}" width="80" height="4" rx="2" fill="{colors.primary}" opacity="0.08"/>'
        )

    @staticmethod
    def _list_shapes(w: int, h: int, colors: any) -> str:
        """Listicle/educational shapes."""
        return (
            f'<rect x="60" y="100" width="12" height="12" rx="3" fill="{colors.primary}" opacity="0.3"/>'
            f'<rect x="60" y="130" width="12" height="12" rx="3" fill="{colors.primary}" opacity="0.15"/>'
            f'<rect x="60" y="160" width="12" height="12" rx="3" fill="{colors.primary}" opacity="0.08"/>'
        )

    @staticmethod
    def _glass_shapes(w: int, h: int, colors: any) -> str:
        """Glassmorphism decorative shapes."""
        return (
            f'<rect x="40" y="40" width="{w-80}" height="{h-80}" rx="40" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>'
            f'<rect x="60" y="60" width="{w-120}" height="{h-120}" rx="30" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>'
        )

    @staticmethod
    def _hero_shapes(w: int, h: int, colors: any) -> str:
        """Hero layout shapes."""
        return (
            f'<rect x="0" y="0" width="{w}" height="{h*0.55}" fill="{colors.primary}" opacity="0.03"/>'
            f'<line x1="0" y1="{h*0.55}" x2="{w}" y2="{h*0.55}" stroke="{colors.primary}" stroke-width="2" opacity="0.15"/>'
        )

    @staticmethod
    def _bottom_bar(w: int, h: int, colors: any, template: str) -> str:
        """Bottom accent bar."""
        if template in ("minimal", "business", "infographic", "education"):
            return (
                f'<rect x="60" y="{h-80}" width="40" height="3" rx="1.5" fill="{colors.primary}" opacity="0.4"/>'
                f'<rect x="110" y="{h-80}" width="20" height="3" rx="1.5" fill="{colors.primary}" opacity="0.2"/>'
            )
        return ""

    @staticmethod
    def generate_number_badge(number: int, x: int, y: int, size: int, color: str) -> str:
        """Generate a number badge for listicles."""
        return (
            f'<circle cx="{x}" cy="{y}" r="{size//2}" fill="{color}" opacity="0.15"/>'
            f'<text x="{x}" y="{y+size//4}" text-anchor="middle" font-size="{size//2}" font-weight="800" fill="{color}">{number}</text>'
        )