"""
Background Engine — generates all background types programmatically.

Supports:
- Solid colors
- Linear/radial gradients
- Mesh gradients
- SVG patterns (dots, lines, grid, wave)
- Geometric shapes
- Glass panels with blur
- Noise textures
- Abstract shapes
- Wave patterns
"""

from dataclasses import dataclass
from typing import Optional

from packages.graphic_engine.src.engine.spec import BackgroundSpec, ColorPalette, DesignSpec


class BackgroundEngine:
    """Generates SVG background markup for any design."""

    @staticmethod
    def generate_svg(spec: DesignSpec) -> str:
        """Generate the full SVG background markup."""
        bg = spec.background
        colors = spec.colors
        w, h = spec.layout.width, spec.layout.height

        bg_type = bg.background_type
        markup = f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">'

        if bg_type == "solid":
            markup += BackgroundEngine._solid(colors.background)
        elif bg_type == "gradient":
            markup += BackgroundEngine._gradient(bg, colors)
        elif bg_type == "mesh":
            markup += BackgroundEngine._mesh(bg, colors, w, h)
        elif bg_type == "pattern":
            markup += BackgroundEngine._pattern(bg, colors, w, h)
        elif bg_type == "glass":
            markup += BackgroundEngine._glass(bg, colors, w, h)
        elif bg_type == "geometric":
            markup += BackgroundEngine._geometric(bg, colors, w, h)
        elif bg_type == "abstract":
            markup += BackgroundEngine._abstract(bg, colors, w, h)
        elif bg_type == "noise":
            markup += BackgroundEngine._noise(colors, w, h)
        elif bg_type == "wave":
            markup += BackgroundEngine._wave(bg, colors, w, h)
        else:
            markup += BackgroundEngine._solid(colors.background)

        markup += '</svg>'
        return markup

    @staticmethod
    def _solid(color: str) -> str:
        return f'<rect width="100%" height="100%" fill="{color}"/>'

    @staticmethod
    def _gradient(bg: BackgroundSpec, colors: ColorPalette) -> str:
        c = bg.gradient_colors
        if len(c) < 2:
            c = [colors.primary, colors.secondary]
        angle = bg.gradient_angle
        # Convert angle to x1/y1/x2/y2
        rad = math.radians(angle)
        x1 = 0.5 - 0.5 * math.cos(rad)
        y1 = 0.5 - 0.5 * math.sin(rad)
        x2 = 0.5 + 0.5 * math.cos(rad)
        y2 = 0.5 + 0.5 * math.sin(rad)

        stops = "".join(f'<stop offset="{i/(len(c)-1)*100}%" stop-color="{col}"/>'
                        for i, col in enumerate(c))
        return (
            f'<defs><linearGradient id="bg-grad" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{stops}</linearGradient></defs>'
            f'<rect width="100%" height="100%" fill="url(#bg-grad)"/>'
        )

    @staticmethod
    def _mesh(bg: BackgroundSpec, colors: ColorPalette, w: int, h: int) -> str:
        """Mesh gradient — multiple blurred circles."""
        cols = bg.mesh_colors or [colors.primary, colors.accent, colors.background]
        circles = ""
        positions = [(0.2, 0.3), (0.8, 0.7), (0.5, 0.2), (0.3, 0.8), (0.7, 0.4)]
        for i, col in enumerate(cols[:5]):
            x, y = positions[i % len(positions)]
            circles += (
                f'<circle cx="{x*w}" cy="{y*h}" r="{max(w,h)*0.4}" '
                f'fill="{col}" opacity="0.3" filter="url(#blur-mesh)"/>'
            )
        return (
            f'<defs><filter id="blur-mesh"><feGaussianBlur stdDeviation="{max(w,h)*0.08}"/></filter></defs>'
            f'<rect width="100%" height="100%" fill="{colors.background}"/>'
            f'{circles}'
        )

    @staticmethod
    def _pattern(bg: BackgroundSpec, colors: ColorPalette, w: int, h: int) -> str:
        """SVG pattern overlay."""
        p_color = bg.pattern_color or "rgba(255,255,255,0.05)"
        pattern_type = bg.pattern_type or "dots"

        pattern_svg = ""
        if pattern_type == "dots":
            pattern_svg = '<pattern id="pat" width="20" height="20" patternUnits="userSpaceOnUse">'
            pattern_svg += f'<circle cx="10" cy="10" r="1.5" fill="{p_color}"/></pattern>'
        elif pattern_type == "lines":
            pattern_svg = '<pattern id="pat" width="40" height="40" patternUnits="userSpaceOnUse">'
            pattern_svg += f'<line x1="0" y1="0" x2="40" y2="40" stroke="{p_color}" stroke-width="1"/></pattern>'
        elif pattern_type == "grid":
            pattern_svg = '<pattern id="pat" width="30" height="30" patternUnits="userSpaceOnUse">'
            pattern_svg += f'<rect width="30" height="30" fill="none" stroke="{p_color}" stroke-width="0.5"/></pattern>'
        elif pattern_type == "waves":
            pattern_svg = '<pattern id="pat" width="100" height="20" patternUnits="userSpaceOnUse">'
            pattern_svg += f'<path d="M0 10 Q25 0 50 10 Q75 20 100 10" fill="none" stroke="{p_color}" stroke-width="1"/></pattern>'

        return (
            f'<defs>{pattern_svg}</defs>'
            f'<rect width="100%" height="100%" fill="{colors.background}"/>'
            f'<rect width="100%" height="100%" fill="url(#pat)"/>'
        )

    @staticmethod
    def _glass(bg: BackgroundSpec, colors: ColorPalette, w: int, h: int) -> str:
        """Glassmorphism background with blur and gradient."""
        opacity = bg.glass_opacity or 0.1
        blur = bg.blur_amount or 20
        return (
            f'<defs>'
            f'<linearGradient id="glass-grad" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0%" stop-color="{colors.primary}" stop-opacity="0.2"/>'
            f'<stop offset="100%" stop-color="{colors.accent}" stop-opacity="0.1"/>'
            f'</linearGradient>'
            f'<filter id="glass-blur"><feGaussianBlur stdDeviation="{blur}"/></filter>'
            f'<filter id="glass-noise"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" result="noise"/><feColorMatrix type="saturate" values="0" in="noise" result="grayNoise"/><feBlend in="SourceGraphic" in2="grayNoise" mode="multiply"/></filter>'
            f'</defs>'
            f'<rect width="100%" height="100%" fill="{colors.background}"/>'
            f'<rect width="100%" height="100%" fill="url(#glass-grad)" opacity="0.8"/>'
            f'<circle cx="{w*0.2}" cy="{h*0.3}" r="{w*0.3}" fill="{colors.primary}" opacity="{opacity}" filter="url(#glass-blur)"/>'
            f'<circle cx="{w*0.8}" cy="{h*0.7}" r="{w*0.25}" fill="{colors.accent}" opacity="{opacity}" filter="url(#glass-blur)"/>'
            f'<circle cx="{w*0.5}" cy="{h*0.9}" r="{w*0.2}" fill="{colors.secondary}" opacity="{opacity}" filter="url(#glass-blur)"/>'
        )

    @staticmethod
    def _geometric(bg: BackgroundSpec, colors: ColorPalette, w: int, h: int) -> str:
        """Geometric shapes background."""
        return (
            f'<rect width="100%" height="100%" fill="{colors.background}"/>'
            f'<polygon points="{w*0.1},{h*0.1} {w*0.15},{h*0.05} {w*0.2},{h*0.1} {w*0.15},{h*0.15}" fill="{colors.primary}" opacity="0.1"/>'
            f'<polygon points="{w*0.8},{h*0.8} {w*0.9},{h*0.75} {w*0.85},{h*0.9}" fill="{colors.accent}" opacity="0.1"/>'
            f'<rect x="{w*0.05}" y="{h*0.85}" width="{w*0.15}" height="{w*0.15}" fill="{colors.primary}" opacity="0.05" transform="rotate(45)"/>'
            f'<circle cx="{w*0.9}" cy="{h*0.15}" r="30" fill="{colors.accent}" opacity="0.08"/>'
            f'<circle cx="{w*0.1}" cy="{h*0.7}" r="50" fill="{colors.primary}" opacity="0.05"/>'
        )

    @staticmethod
    def _abstract(bg: BackgroundSpec, colors: ColorPalette, w: int, h: int) -> str:
        """Abstract organic shapes background."""
        return (
            f'<rect width="100%" height="100%" fill="{colors.background}"/>'
            f'<path d="M0 {h*0.6} Q{w*0.3} {h*0.4} {w*0.5} {h*0.5} T{w} {h*0.3} L{w} {h} L0 {h}Z" fill="{colors.primary}" opacity="0.06"/>'
            f'<path d="M0 {h*0.8} Q{w*0.4} {h*0.6} {w*0.6} {h*0.7} T{w} {h*0.5} L{w} {h} L0 {h}Z" fill="{colors.accent}" opacity="0.04"/>'
            f'<circle cx="{w*0.15}" cy="{h*0.2}" r="{w*0.12}" fill="{colors.primary}" opacity="0.08"/>'
            f'<circle cx="{w*0.85}" cy="{h*0.8}" r="{w*0.15}" fill="{colors.accent}" opacity="0.06"/>'
        )

    @staticmethod
    def _noise(colors: ColorPalette, w: int, h: int) -> str:
        """Noise texture overlay."""
        return (
            f'<rect width="100%" height="100%" fill="{colors.background}"/>'
            f'<filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/><feColorMatrix type="saturate" values="0"/></filter>'
            f'<rect width="100%" height="100%" filter="url(#noise)" opacity="0.03"/>'
        )

    @staticmethod
    def _wave(bg: BackgroundSpec, colors: ColorPalette, w: int, h: int) -> str:
        """Wave pattern background."""
        return (
            f'<rect width="100%" height="100%" fill="{colors.background}"/>'
            f'<path d="M0 {h*0.7} Q{w*0.25} {h*0.65} {w*0.5} {h*0.72} T{w} {h*0.68} L{w} {h} L0 {h}Z" fill="{colors.primary}" opacity="0.08"/>'
            f'<path d="M0 {h*0.78} Q{w*0.3} {h*0.72} {w*0.6} {h*0.8} T{w} {h*0.75} L{w} {h} L0 {h}Z" fill="{colors.accent}" opacity="0.05"/>'
        )


import math  # noqa: E402 — needed for gradient angle calculation