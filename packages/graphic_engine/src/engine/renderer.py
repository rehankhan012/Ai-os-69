"""
GraphicRenderer — transforms a DesignSpec into a final SVG graphic.

Assembles:
- Background (background engine)
- Decorative shapes (shape engine)
- Icon (icon engine)
- Headline + Subheadline
- Body text
- List items (for listicles)
- CTA button
- Branding footer

Output: SVG string ready for PNG conversion or direct display.
"""

import html
from typing import Optional

from packages.graphic_engine.src.engine.spec import DesignSpec, LayoutSpec
from packages.graphic_engine.src.backgrounds.engine import BackgroundEngine
from packages.graphic_engine.src.shapes.engine import ShapeEngine
from packages.graphic_engine.src.icons.engine import IconEngine
from packages.graphic_engine.src.typography.engine import TypographyEngine
from packages.graphic_engine.src.branding.engine import BrandingEngine


class GraphicRenderer:
    """
    Transforms a DesignSpec into a finished SVG graphic.

    This is the core rendering engine. It assembles all components
    into a single SVG that can be displayed in-browser or exported to PNG.
    """

    def __init__(self):
        self.background_engine = BackgroundEngine()
        self.shape_engine = ShapeEngine()
        self.icon_engine = IconEngine()
        self.typography_engine = TypographyEngine()
        self.branding_engine = BrandingEngine()

    def render(self, spec: DesignSpec) -> str:
        """Render a complete SVG from a DesignSpec."""
        w, h = spec.layout.width, spec.layout.height
        colors = spec.colors

        # Build SVG parts
        svg_parts = []

        # 1. SVG opening with Google Fonts import
        svg_parts.append(
            f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink">'
        )

        # 2. Font imports
        svg_parts.append(self._font_imports(spec))

        # 3. Background
        svg_parts.append(self.background_engine.generate_svg(spec))

        # 4. Decorative shapes
        svg_parts.append(self.shape_engine.generate_shapes(spec))

        # 5. Icon
        icon_markup = self._render_icon(spec)
        if icon_markup:
            svg_parts.append(icon_markup)

        # 6. Content blocks
        content_markup = self._render_content(spec)
        svg_parts.append(content_markup)

        # 7. CTA Button
        svg_parts.append(self._render_cta(spec))

        # 8. Branding footer
        svg_parts.append(self.branding_engine.generate_branding_overlay(spec))

        # 9. Close SVG
        svg_parts.append('</svg>')

        return "\n".join(svg_parts)

    def _font_imports(self, spec: DesignSpec) -> str:
        """Generate font import markup."""
        fonts = set()
        fonts.add(spec.typography.headline_font)
        fonts.add(spec.typography.body_font)
        fonts.add(spec.typography.cta_font)

        font_families = "|".join(f.replace(" ", "+") for f in fonts)
        return (
            f'<defs>'
            f'<style>@import url("https://fonts.googleapis.com/css2?family={font_families}:wght@300;400;500;600;700;800;900&display=swap");</style>'
            f'</defs>'
        )

    def _render_icon(self, spec: DesignSpec) -> str:
        """Render the icon if specified."""
        if not spec.icon.icon_category:
            return ""
        w, h = spec.layout.width, spec.layout.height
        icon_size = spec.icon.icon_size
        icon_svg = self.icon_engine.get_category_icon(
            spec.icon.icon_category, icon_size, spec.colors.primary
        )

        # Position icon
        icon_x = (w - icon_size) // 2
        icon_y = spec.layout.safe_zone_top + 20

        # Embed icon SVG inline
        return (
            f'<g transform="translate({icon_x}, {icon_y})">'
            f'{icon_svg}'
            f'</g>'
        )

    def _render_content(self, spec: DesignSpec) -> str:
        """Render headline, subheadline, body text, and list items."""
        w, h = spec.layout.width, spec.layout.height
        content = spec.content
        typography = spec.typography
        layout = spec.layout
        colors = spec.colors

        parts = []
        safe_top = layout.safe_zone_top
        safe_left = layout.safe_zone_left
        content_width = layout.content_area_width

        # Determine if we have an icon
        has_icon = bool(spec.icon.icon_category)
        icon_offset = 100 if has_icon else 0

        # Calculate Y positions
        if layout.layout_type == "hero":
            headline_y = int(h * 0.35)
            sub_y = headline_y + 80
            body_y = sub_y + 60
        elif layout.layout_type in ("split", "split_top"):
            headline_y = int(h * 0.25)
            sub_y = headline_y + 70
            body_y = sub_y + 50
        elif layout.layout_type in ("split_left", "split_right"):
            headline_y = int(h * 0.3)
            sub_y = headline_y + 70
            body_y = sub_y + 50
            # Text aligned left
            typography.headline_alignment = "left"
        else:
            headline_y = int(h * 0.38) + icon_offset
            sub_y = headline_y + 80
            body_y = sub_y + 60

        # Color override for dark backgrounds
        text_color = typography.headline_color
        if spec.background.background_type in ("gradient", "mesh", "glass") and \
           colors.background in ("#0F172A", "#1A1A2E", "#1E1B4B"):
            text_color = "#FFFFFF"
            typography.headline_color = "#FFFFFF"
            typography.body_color = "#CCCCCC"

        # Wrap text
        wrapped_lines = self.typography_engine.word_wrap(
            content.headline, typography.max_line_length_chars
        )

        # Render headline with wrapping support
        line_height = typography.headline_size_px * typography.headline_line_height
        current_y = headline_y

        for line in wrapped_lines[:3]:  # Max 3 lines
            parts.append(self._text_element(
                line, w // 2, current_y, typography.headline_font,
                typography.headline_size_px, typography.headline_weight,
                text_color, typography.headline_alignment, "middle"
            ))
            current_y += line_height

        # Subheadline
        if content.subheadline:
            parts.append(self._text_element(
                content.subheadline, w // 2, current_y + 20,
                typography.subheadline_font, typography.subheadline_size_px,
                typography.subheadline_weight, typography.subheadline_color,
                typography.subheadline_alignment, "middle"
            ))

        # Body text
        if content.body_text:
            body_y_pos = current_y + 60
            for line in content.body_text[:3]:
                parts.append(self._text_element(
                    line, w // 2, body_y_pos, typography.body_font,
                    typography.body_size_px, typography.body_weight,
                    typography.body_color, "center", "middle"
                ))
                body_y_pos += typography.body_size_px * 1.6

        # List items (for listicles)
        if content.list_items:
            list_y = max(current_y + 80, int(h * 0.5))
            for i, item in enumerate(content.list_items[:5]):
                bullet_y = list_y + i * 45
                # Bullet circle
                parts.append(
                    f'<circle cx="{w//2 - 130}" cy="{bullet_y - 5}" '
                    f'r="4" fill="{typography.cta_background}" opacity="0.6"/>'
                )
                # Item text
                parts.append(self._text_element(
                    item, w // 2 - 110, bullet_y, typography.body_font,
                    typography.body_size_px, "500", text_color, "left", "start"
                ))

        return "\n".join(parts)

    def _render_cta(self, spec: DesignSpec) -> str:
        """Render the call-to-action button."""
        w, h = spec.layout.width, spec.layout.height
        typography = spec.typography
        content = spec.content

        cta_text = content.cta or "Save for Later"
        cta_width = len(cta_text) * (typography.cta_size_px * 0.6) + 40
        cta_width = max(140, min(cta_width, 400))
        cta_x = (w - cta_width) // 2
        cta_y = h - 150

        return (
            f'<rect x="{cta_x}" y="{cta_y}" width="{cta_width}" height="44" '
            f'rx="22" fill="{typography.cta_background}" opacity="0.95"/>'
            f'<text x="{w//2}" y="{cta_y + 28}" text-anchor="middle" '
            f'font-family="{typography.cta_font}" font-size="{typography.cta_size_px}" '
            f'font-weight="{typography.cta_weight}" fill="{typography.cta_color}">'
            f'{html.escape(cta_text)}</text>'
        )

    def _text_element(self, text: str, x: int, y: int, font: str, size: int,
                       weight: str, color: str, alignment: str,
                       anchor: str = "middle") -> str:
        """Generate an SVG text element."""
        return (
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
            f'font-family="{font}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}" '
            f'text-align="{alignment}">{html.escape(text)}</text>'
        )