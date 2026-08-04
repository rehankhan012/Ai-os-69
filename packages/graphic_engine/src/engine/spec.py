"""
DesignSpec — the structured design specification.

This is the output of the AI design decision process and the input
to the GraphicRenderer. Every design decision is captured here.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ColorPalette:
    """Color palette for a design."""
    primary: str = "#E94560"       # Main brand color
    secondary: str = "#1A1A2E"     # Dark contrast
    accent: str = "#0F3460"        # Highlight
    background: str = "#FFFFFF"    # Background
    text: str = "#1A1A2E"          # Text color
    text_light: str = "#666666"    # Secondary text
    surface: str = "#F5F5F5"       # Card/surface color
    gradient_start: str = ""       # Gradient start (if used)
    gradient_end: str = ""         # Gradient end (if used)


@dataclass
class TypographySpec:
    """Typography decisions for a design."""
    headline_font: str = "Inter"
    headline_weight: str = "800"
    headline_size_px: int = 52
    headline_color: str = "#1A1A2E"
    headline_alignment: str = "center"
    headline_line_height: float = 1.2

    subheadline_font: str = "Inter"
    subheadline_weight: str = "600"
    subheadline_size_px: int = 28
    subheadline_color: str = "#666666"
    subheadline_alignment: str = "center"

    body_font: str = "Inter"
    body_weight: str = "400"
    body_size_px: int = 18
    body_color: str = "#444444"
    body_alignment: str = "center"
    body_line_height: float = 1.5

    cta_font: str = "Inter"
    cta_weight: str = "700"
    cta_size_px: int = 16
    cta_color: str = "#FFFFFF"
    cta_background: str = "#E94560"
    cta_text: str = "Save for Later"

    max_line_length_chars: int = 40
    readability_score: float = 90.0


@dataclass
class LayoutSpec:
    """Layout structure for the canvas."""
    width: int = 1000
    height: int = 1500
    safe_zone_top: int = 80
    safe_zone_bottom: int = 80
    safe_zone_left: int = 60
    safe_zone_right: int = 60
    content_area_width: int = 880
    content_area_height: int = 1340

    layout_type: str = "centered"  # centered, split_top, split_bottom, split_left, split_right, magazine, hero, listicle, card_grid

    headline_y: int = 400
    headline_x: int = 500
    body_y: int = 600
    cta_y: int = 1300


@dataclass
class BackgroundSpec:
    """Background design choices."""
    background_type: str = "gradient"  # solid, gradient, pattern, mesh, glass, abstract, geometric, noise, wave
    gradient_angle: int = 135
    gradient_colors: list[str] = field(default_factory=lambda: ["#667eea", "#764ba2"])
    pattern_type: str = "dots"         # dots, lines, grid, crosshatch, waves
    pattern_color: str = "rgba(255,255,255,0.05)"
    mesh_colors: list[str] = field(default_factory=lambda: ["#667eea", "#764ba2", "#f093fb"])
    has_glass_panel: bool = False
    glass_opacity: float = 0.1
    blur_amount: int = 20


@dataclass
class ShapeSpec:
    """Decorative shapes in the design."""
    shapes: list[dict] = field(default_factory=list)
    # Each shape: {"type": "circle", "x": 100, "y": 200, "radius": 50, "color": "#eee", "opacity": 0.3}


@dataclass
class IconSpec:
    """Icons in the design."""
    icon_category: str = ""          # technology, finance, food, travel, etc.
    icon_name: str = ""              # Specific icon name
    icon_position: str = "top"       # top, center, bottom
    icon_size: int = 80
    icon_color: str = "#E94560"


@dataclass
class BrandingSpec:
    """Branding overlay."""
    logo_url: Optional[str] = None
    website: str = ""
    social_handle: str = ""
    show_footer: bool = True
    footer_text: str = "Follow for more tips"
    watermark_opacity: float = 0.3


@dataclass
class ContentSpec:
    """The actual content to render on the pin."""
    headline: str = "Your Headline Here"
    subheadline: str = ""
    body_text: list[str] = field(default_factory=list)
    cta: str = "Save for Later"
    hashtags: list[str] = field(default_factory=list)
    list_items: list[str] = field(default_factory=list)
    keyword: str = ""


@dataclass
class DesignSpec:
    """
    Complete design specification.
    Every design decision is captured here for the renderer.
    """
    content: ContentSpec = field(default_factory=ContentSpec)
    colors: ColorPalette = field(default_factory=ColorPalette)
    typography: TypographySpec = field(default_factory=TypographySpec)
    layout: LayoutSpec = field(default_factory=LayoutSpec)
    background: BackgroundSpec = field(default_factory=BackgroundSpec)
    shapes: ShapeSpec = field(default_factory=ShapeSpec)
    icon: IconSpec = field(default_factory=IconSpec)
    branding: BrandingSpec = field(default_factory=BrandingSpec)

    template_name: str = "modern"
    variation_name: str = "A"
    quality_score: float = 0.0
    design_rationale: str = ""
    render_time_ms: float = 0.0


class DesignSpecBuilder:
    """Fluent builder for constructing DesignSpec objects."""

    def __init__(self):
        self.spec = DesignSpec()

    def with_content(self, headline: str = "", subheadline: str = "",
                     body: list[str] | None = None, cta: str = "",
                     hashtags: list[str] | None = None,
                     list_items: list[str] | None = None,
                     keyword: str = "") -> "DesignSpecBuilder":
        self.spec.content = ContentSpec(
            headline=headline,
            subheadline=subheadline,
            body_text=body or [],
            cta=cta or "Save for Later",
            hashtags=hashtags or [],
            list_items=list_items or [],
            keyword=keyword,
        )
        return self

    def with_colors(self, primary: str = "#E94560", secondary: str = "#1A1A2E",
                    accent: str = "#0F3460", background: str = "#FFFFFF",
                    text: str = "#1A1A2E") -> "DesignSpecBuilder":
        self.spec.colors = ColorPalette(
            primary=primary, secondary=secondary, accent=accent,
            background=background, text=text,
        )
        return self

    def with_typography(self, headline_font: str = "Inter", headline_size: int = 52,
                        body_size: int = 18, alignment: str = "center") -> "DesignSpecBuilder":
        self.spec.typography.headline_font = headline_font
        self.spec.typography.headline_size_px = headline_size
        self.spec.typography.body_size_px = body_size
        self.spec.typography.headline_alignment = alignment
        return self

    def with_layout(self, layout_type: str = "centered") -> "DesignSpecBuilder":
        self.spec.layout.layout_type = layout_type
        return self

    def with_background_gradient(self, colors: list[str] | None = None,
                                  angle: int = 135) -> "DesignSpecBuilder":
        self.spec.background.background_type = "gradient"
        self.spec.background.gradient_colors = colors or ["#667eea", "#764ba2"]
        self.spec.background.gradient_angle = angle
        return self

    def with_background_glass(self) -> "DesignSpecBuilder":
        self.spec.background.background_type = "glass"
        self.spec.background.has_glass_panel = True
        return self

    def with_icon(self, category: str, size: int = 80) -> "DesignSpecBuilder":
        self.spec.icon.icon_category = category
        self.spec.icon.icon_size = size
        return self

    def with_branding(self, website: str = "", handle: str = "") -> "DesignSpecBuilder":
        self.spec.branding.website = website
        self.spec.branding.social_handle = handle
        return self

    def with_template(self, name: str) -> "DesignSpecBuilder":
        self.spec.template_name = name
        return self

    def build(self) -> DesignSpec:
        return self.spec