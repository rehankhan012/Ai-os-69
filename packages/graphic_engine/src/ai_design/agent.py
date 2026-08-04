"""
AI Design Agent — the brain of the graphic engine.

Given a topic, it decides:
- Which template to use (and why)
- Layout structure
- Typography (fonts, sizes, weights)
- Color palette
- Background style
- Shapes and decorations
- Icon choice and placement
- CTA placement
- Branding overlay

It evaluates every design and can redesign if quality is poor.
"""

from typing import Optional

from packages.graphic_engine.src.engine.spec import (
    DesignSpec, DesignSpecBuilder, ContentSpec, ColorPalette,
    TypographySpec, LayoutSpec, BackgroundSpec, ShapeSpec,
    IconSpec, BrandingSpec,
)
from packages.graphic_engine.src.templates.engine import TemplateEngine
from packages.graphic_engine.src.typography.engine import TypographyEngine
from packages.graphic_engine.src.branding.engine import BrandingEngine, BrandProfile


class AIDesignAgent:
    """
    AI Design Agent — makes professional design decisions.

    This agent thinks like a senior graphic designer.
    It evaluates the topic, audience, and mood, then constructs
    a complete design specification ready for rendering.
    """

    def __init__(self):
        self.template_engine = TemplateEngine()
        self.typography_engine = TypographyEngine()
        self.branding_engine = BrandingEngine()

    async def design(self, topic: str, audience: str = "", mood: str = "clean",
                      niche: str = "", brand_color: str = "#2563EB",
                      brand_profile: str = "default", count: int = 3) -> dict:
        """
        Create complete design specifications for a topic.

        Returns multiple design variations.
        """
        # Step 1: Select template
        template_name = self.template_engine.select_template(topic, niche)
        template_info = self.template_engine.get_template_info(template_name)

        # Step 2: Extract or create content
        content = self._extract_content(topic, audience, mood)

        # Step 3: Generate base spec
        base_spec = self.template_engine.generate_spec(
            template_name, content, brand_color
        )

        # Step 4: Apply brand profile
        profile = self.branding_engine.get_profile(brand_profile)
        base_spec = self.branding_engine.apply_brand_profile(base_spec, profile)

        # Step 5: Fine-tune typography
        typography = self.typography_engine.calculate_typography(base_spec)
        base_spec.typography = typography

        # Step 6: Generate variations
        variations = []
        for i in range(count):
            variant = self._create_variation(base_spec, i, count)
            quality = self._evaluate_design(variant)
            variant.quality_score = quality
            variant.variation_name = chr(65 + i)  # A, B, C...
            variations.append(variant)

        # Step 7: Sort by quality (best first)
        variations.sort(key=lambda v: v.quality_score, reverse=True)

        return {
            "template_selected": template_name,
            "template_rationale": template_info["vibe"],
            "variations": [self._spec_to_dict(v) for v in variations],
            "best_variation": chr(65),
            "design_rationale": self._generate_rationale(template_name, topic, niche, mood),
        }

    def _extract_content(self, topic: str, audience: str, mood: str) -> ContentSpec:
        """Extract structured content from the topic."""
        # Try to detect if this is a listicle
        is_list = any(kw in topic.lower() for kw in [" tips", " ways", " steps", " reasons",
                                                       " ideas", " secrets", " tricks", " hacks"])
        is_guide = any(kw in topic.lower() for kw in ["guide", "how to", "complete", "ultimate"])
        is_question = any(kw in topic.lower() for kw in ["why", "how", "what", "when", "which"])
        is_quote = any(kw in topic.lower() for kw in ["quote", "say", "inspiration"])

        # Build list items for listicles
        list_items = []
        if is_list:
            for i in range(1, 6):
                list_items.append(f"{'Tip' if 'tip' in topic.lower() else 'Way'} {i}")

        # Extract CTA
        cta = "Save for Later"
        if is_guide:
            cta = "Save This Guide"
        elif is_question:
            cta = "Learn the Answer"
        elif audience:
            cta = f"Save for {audience.title()}"

        # Build body
        body = [
            f"Perfect for {audience} • Save this pin for later"
        ] if audience else []

        return ContentSpec(
            headline=topic,
            subheadline=f"Best tips for {audience}" if audience else "",
            body_text=body,
            cta=cta,
            list_items=list_items,
            keyword=topic,
        )

    def _create_variation(self, base: DesignSpec, index: int, total: int) -> DesignSpec:
        """Create a design variation with different styling choices."""
        import copy
        variant = copy.deepcopy(base)

        # Vary colors
        if index == 1:
            # Swap primary and accent
            variant.colors.primary, variant.colors.accent = (
                base.colors.accent, base.colors.primary
            )
            variant.typography.headline_size_px = max(36, base.typography.headline_size_px - 4)
        elif index == 2:
            # Different gradient direction
            variant.background.background_type = "mesh"
            variant.typography.body_color = base.colors.text_light
            variant.typography.headline_alignment = "left"
            variant.layout.layout_type = "split"
        elif index == 3:
            # Glass variation
            variant.background.background_type = "glass"
            variant.colors.background = base.colors.secondary
            variant.colors.text = "#FFFFFF"
            variant.colors.text_light = "#AAAAAA"
            variant.typography.headline_color = "#FFFFFF"
            variant.typography.body_color = "#CCCCCC"
        elif index == 4:
            # Inverted colors
            variant.colors.background, variant.colors.text = (
                base.colors.secondary, "#FFFFFF"
            )
            variant.typography.headline_color = "#FFFFFF"
            variant.typography.body_color = "#CCCCCC"

        return variant

    def _evaluate_design(self, spec: DesignSpec) -> float:
        """Evaluate design quality (0-100). Returns score."""
        score = 85.0  # Base score

        # Check headline length
        headline_len = len(spec.content.headline)
        if headline_len > 80:
            score -= 10
        elif headline_len < 10:
            score -= 5

        # Check font sizes
        if spec.typography.headline_size_px < 30:
            score -= 15
        elif spec.typography.headline_size_px > 70:
            score -= 5

        if spec.typography.body_size_px < 14:
            score -= 10

        # Check readability
        readability = spec.typography.readability_score
        score = score * 0.5 + readability * 0.5

        # Check color contrast (basic)
        if spec.colors.background == spec.colors.text:
            score -= 20

        # Reward good structure
        if spec.content.headline and spec.content.cta:
            score += 5

        return max(0, min(100, round(score, 1)))

    def _generate_rationale(self, template: str, topic: str,
                             niche: str, mood: str) -> str:
        """Generate a human-readable explanation of design decisions."""
        return (
            f"Selected '{template}' template for '{topic}' in '{niche}' niche. "
            f"Chose this template because {TemplateEngine.TEMPLATES.get(template, {}).get('vibe', 'it fits the content')}. "
            f"The {mood} mood drives the color palette and spacing decisions. "
            f"Typography was optimized for readability on mobile Pinterest feeds."
        )

    def _spec_to_dict(self, spec: DesignSpec) -> dict:
        """Convert DesignSpec to a serializable dictionary."""
        return {
            "variation": spec.variation_name,
            "quality_score": spec.quality_score,
            "template": spec.template_name,
            "design_rationale": spec.design_rationale,
            "content": {
                "headline": spec.content.headline,
                "subheadline": spec.content.subheadline,
                "body": spec.content.body_text,
                "cta": spec.content.cta,
                "list_items": spec.content.list_items,
            },
            "colors": {
                "primary": spec.colors.primary,
                "secondary": spec.colors.secondary,
                "accent": spec.colors.accent,
                "background": spec.colors.background,
                "text": spec.colors.text,
                "gradient_start": spec.colors.gradient_start,
                "gradient_end": spec.colors.gradient_end,
            },
            "typography": {
                "headline_font": spec.typography.headline_font,
                "headline_size_px": spec.typography.headline_size_px,
                "headline_weight": spec.typography.headline_weight,
                "headline_color": spec.typography.headline_color,
                "headline_alignment": spec.typography.headline_alignment,
                "body_font": spec.typography.body_font,
                "body_size_px": spec.typography.body_size_px,
                "readability_score": spec.typography.readability_score,
            },
            "layout": {
                "type": spec.layout.layout_type,
                "width": spec.layout.width,
                "height": spec.layout.height,
            },
            "background": {
                "type": spec.background.background_type,
                "gradient_colors": spec.background.gradient_colors,
            },
            "branding": {
                "footer_text": spec.branding.footer_text,
                "social_handle": spec.branding.social_handle,
                "show_footer": spec.branding.show_footer,
            },
        }