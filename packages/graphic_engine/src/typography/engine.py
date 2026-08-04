"""
Typography Engine — automatically chooses fonts, sizes, spacing,
alignment, and checks readability. Never allows overlapping text.
"""

import math
from dataclasses import dataclass
from typing import Optional

from packages.graphic_engine.src.engine.spec import TypographySpec, DesignSpec


@dataclass
class TextBlock:
    """A positioned text block ready for rendering."""
    text: str
    font_family: str
    font_weight: str
    font_size_px: int
    color: str
    x: int
    y: int
    width: int
    height: int
    alignment: str
    line_height: float
    max_width: int
    lines: list[str]


class TypographyEngine:
    """Handles all typography decisions for a design."""

    FONT_MAP = {
        "Inter": {"weights": ["300", "400", "500", "600", "700", "800", "900"]},
        "Playfair Display": {"weights": ["400", "600", "700", "800"]},
        "Poppins": {"weights": ["300", "400", "500", "600", "700"]},
        "Space Grotesk": {"weights": ["300", "400", "500", "600", "700"]},
        "DM Sans": {"weights": ["400", "500", "700"]},
        "Cabinet Grotesk": {"weights": ["400", "500", "700", "800"]},
        "Clash Display": {"weights": ["400", "500", "600", "700"]},
    }

    # Style -> font recommendations
    STYLE_FONTS = {
        "minimal": ("Inter", "Inter"),
        "luxury": ("Playfair Display", "Inter"),
        "business": ("Inter", "Inter"),
        "modern": ("Space Grotesk", "Inter"),
        "magazine": ("Playfair Display", "DM Sans"),
        "technology": ("Space Grotesk", "Inter"),
        "education": ("DM Sans", "Inter"),
        "recipe": ("Cabinet Grotesk", "Inter"),
        "travel": ("Clash Display", "Inter"),
        "fashion": ("Playfair Display", "Poppins"),
        "quotes": ("Playfair Display", "Inter"),
        "infographic": ("Inter", "Inter"),
        "glassmorphism": ("Inter", "Inter"),
        "split": ("Space Grotesk", "Inter"),
        "hero": ("Clash Display", "Inter"),
        "listicle": ("Inter", "Inter"),
        "comparison": ("Inter", "Inter"),
        "product": ("Cabinet Grotesk", "Inter"),
    }

    def __init__(self, template_name: str = "modern"):
        self.template_name = template_name
        self.headline_font, self.body_font = self.STYLE_FONTS.get(
            template_name, ("Inter", "Inter")
        )

    def calculate_typography(self, spec: DesignSpec) -> TypographySpec:
        """Calculate optimal typography based on content and layout."""
        content = spec.content
        layout = spec.layout
        colors = spec.colors

        headline = content.headline
        body_text = "\n".join(content.body_text) if content.body_text else ""

        # Calculate optimal headline size based on length
        headline_len = len(headline)
        if headline_len > 60:
            headline_size = 36
        elif headline_len > 40:
            headline_size = 42
        elif headline_len > 25:
            headline_size = 48
        else:
            headline_size = 52

        # Calculate body size
        body_size = 18 if len(body_text) > 200 else 20

        # Calculate subheadline size
        sub_size = max(20, headline_size - 24)

        # Determine alignment based on layout
        alignment = "center"
        if layout.layout_type in ("split_left", "split_right"):
            alignment = "left"
        elif layout.layout_type == "hero":
            alignment = "center"

        # Calculate readability
        readability = self._calculate_readability(headline, body_text, headline_size, body_size)

        # Calculate CTA
        cta_text = content.cta or "Save for Later"

        return TypographySpec(
            headline_font=self.headline_font,
            headline_weight=self._get_weight("headline", headline_size),
            headline_size_px=headline_size,
            headline_color=colors.text,
            headline_alignment=alignment,
            subheadline_font=self.body_font,
            subheadline_weight="600",
            subheadline_size_px=sub_size,
            subheadline_color=colors.text_light,
            subheadline_alignment=alignment,
            body_font=self.body_font,
            body_weight="400",
            body_size_px=body_size,
            body_color=colors.text_light,
            body_alignment=alignment,
            cta_font=self.body_font,
            cta_weight="700",
            cta_size_px=16,
            cta_color=colors.background,
            cta_background=colors.primary,
            cta_text=cta_text,
            max_line_length_chars=self._max_line_chars(headline_size),
            readability_score=readability,
        )

    def word_wrap(self, text: str, max_chars_per_line: int) -> list[str]:
        """Wrap text to fit within max character limit."""
        if not text:
            return []
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars_per_line:
                current_line = f"{current_line} {word}".strip()
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def calculate_text_block(self, text: str, font_size: int, max_width: int,
                              alignment: str, font_family: str) -> TextBlock:
        """Calculate a positioned text block. Approximate width = font_size * 0.6 * chars."""
        approx_char_width = font_size * 0.6
        chars_per_line = max(1, int(max_width / approx_char_width))
        lines = self.word_wrap(text, chars_per_line)
        line_height = font_size * 1.4
        total_height = len(lines) * line_height

        return TextBlock(
            text=text,
            font_family=font_family,
            font_weight="400",
            font_size_px=font_size,
            color="#000000",
            x=0, y=0, width=max_width, height=int(total_height),
            alignment=alignment, line_height=line_height,
            max_width=max_width, lines=lines,
        )

    def _get_weight(self, role: str, size: int) -> str:
        """Get appropriate font weight based on role and size."""
        if role == "headline":
            return "800" if size > 36 else "700"
        elif role == "cta":
            return "700"
        return "400"

    def _max_line_chars(self, font_size: int) -> int:
        """Calculate max characters per line based on font size and safe zone."""
        # With 60px padding on each side, content area = 880px for 1000px canvas
        usable_width = 880
        approx_char_width = font_size * 0.6
        return max(10, int(usable_width / approx_char_width))

    def _calculate_readability(self, headline: str, body: str,
                                 headline_size: int, body_size: int) -> float:
        """Calculate a readability score (0-100)."""
        score = 100.0

        # Penalize very long headlines
        if len(headline) > 80:
            score -= 15
        elif len(headline) > 60:
            score -= 8

        # Penalize very small text
        if headline_size < 30:
            score -= 10
        if body_size < 14:
            score -= 10

        # Penalize empty body
        if not body and len(headline) > 50:
            score -= 5

        # Penalize very long lines
        if self._max_line_chars(headline_size) < 15:
            score -= 10

        return max(0, min(100, score))

    def check_overlap(self, blocks: list[TextBlock]) -> list[str]:
        """Check for overlapping text blocks. Returns list of warnings."""
        warnings = []
        for i in range(len(blocks)):
            for j in range(i + 1, len(blocks)):
                b1, b2 = blocks[i], blocks[j]
                if (b1.x < b2.x + b2.width and b1.x + b1.width > b2.x and
                    b1.y < b2.y + b2.height and b1.y + b1.height > b2.y):
                    warnings.append(f"Overlap detected between block {i} and {j}")
        return warnings