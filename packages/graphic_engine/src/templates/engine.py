"""
Template Engine — maps content to design specifications.

18 layouts:
minimal, luxury, business, modern, magazine, glassmorphism,
technology, education, recipe, travel, fashion, quotes,
infographic, product, comparison, listicle, split, hero
"""

from typing import Optional

from packages.graphic_engine.src.engine.spec import (
    DesignSpec, DesignSpecBuilder, ContentSpec, ColorPalette,
    TypographySpec, LayoutSpec, BackgroundSpec, IconSpec, BrandingSpec
)


class TemplateEngine:
    """Maps topics/niches to templates and generates DesignSpecs."""

    TEMPLATES = {
        "minimal": {
            "name": "Minimal",
            "background": "solid",
            "layout": "centered",
            "vibe": "Clean, professional, whitespace-dominant",
            "best_for": ["business", "professional", "corporate", "consulting"],
        },
        "luxury": {
            "name": "Luxury",
            "background": "gradient",
            "layout": "centered",
            "vibe": "Elegant, premium, gold accents",
            "best_for": ["fashion", "jewelry", "high-end", "premium", "exclusive"],
        },
        "business": {
            "name": "Business",
            "background": "solid",
            "layout": "centered",
            "vibe": "Professional, structured, trustworthy",
            "best_for": ["business", "startup", "entrepreneur", "b2b", "finance"],
        },
        "modern": {
            "name": "Modern",
            "background": "gradient",
            "layout": "centered",
            "vibe": "Sleek, contemporary, bold",
            "best_for": ["technology", "design", "creative", "agency"],
        },
        "magazine": {
            "name": "Magazine",
            "background": "solid",
            "layout": "split_top",
            "vibe": "Editorial, sophisticated, bold typography",
            "best_for": ["fashion", "lifestyle", "culture", "art"],
        },
        "glassmorphism": {
            "name": "Glassmorphism",
            "background": "glass",
            "layout": "centered",
            "vibe": "Modern, frosted glass, depth",
            "best_for": ["technology", "ai", "software", "modern"],
        },
        "technology": {
            "name": "Technology",
            "background": "geometric",
            "layout": "centered",
            "vibe": "Tech-forward, digital, innovative",
            "best_for": ["tech", "software", "coding", "ai", "digital"],
        },
        "education": {
            "name": "Education",
            "background": "pattern",
            "layout": "centered",
            "vibe": "Academic, clear, structured",
            "best_for": ["education", "learning", "teaching", "how-to", "guide"],
        },
        "recipe": {
            "name": "Recipe",
            "background": "solid",
            "layout": "split_bottom",
            "vibe": "Warm, appetizing, lifestyle",
            "best_for": ["recipe", "food", "cooking", "baking", "nutrition"],
        },
        "travel": {
            "name": "Travel",
            "background": "gradient",
            "layout": "hero",
            "vibe": "Adventurous, vibrant, inspiring",
            "best_for": ["travel", "adventure", "explore", "wanderlust"],
        },
        "fashion": {
            "name": "Fashion",
            "background": "solid",
            "layout": "split_left",
            "vibe": "Chic, stylish, elegant",
            "best_for": ["fashion", "style", "beauty", "wardrobe"],
        },
        "quotes": {
            "name": "Quotes",
            "background": "gradient",
            "layout": "centered",
            "vibe": "Inspirational, motivational, typography-focused",
            "best_for": ["quotes", "inspiration", "motivation", "mindset"],
        },
        "infographic": {
            "name": "Infographic",
            "background": "solid",
            "layout": "listicle",
            "vibe": "Data-driven, organized, visual",
            "best_for": ["data", "statistics", "how-to", "guide", "tips"],
        },
        "product": {
            "name": "Product Showcase",
            "background": "gradient",
            "layout": "split_right",
            "vibe": "Product-focused, clean, commercial",
            "best_for": ["product", "ecommerce", "sale", "offer"],
        },
        "comparison": {
            "name": "Comparison",
            "background": "solid",
            "layout": "split",
            "vibe": "Comparative, balanced, clear",
            "best_for": ["comparison", "vs", "versus", "alternative"],
        },
        "listicle": {
            "name": "Listicle",
            "background": "solid",
            "layout": "listicle",
            "vibe": "Scannable, numbered, actionable",
            "best_for": ["tips", "list", "top", "best", "ways", "steps"],
        },
        "split": {
            "name": "Split Layout",
            "background": "gradient",
            "layout": "split",
            "vibe": "Modern, balanced, dual-tone",
            "best_for": ["comparison", "before-after", "transform"],
        },
        "hero": {
            "name": "Hero Layout",
            "background": "gradient",
            "layout": "hero",
            "vibe": "Bold, dramatic, attention-grabbing",
            "best_for": ["announcement", "launch", "big-idea", "statement"],
        },
    }

    # Auto-select template based on niche/topic
    NICHE_TEMPLATE_MAP = {
        "tech": "technology", "technology": "technology",
        "ai": "technology", "software": "technology",
        "coding": "technology", "programming": "technology",
        "business": "business", "startup": "business",
        "entrepreneur": "business", "finance": "business",
        "marketing": "business", "seo": "business",
        "fashion": "fashion", "style": "fashion",
        "beauty": "fashion", "luxury": "luxury",
        "food": "recipe", "recipe": "recipe",
        "cooking": "recipe", "baking": "recipe",
        "travel": "travel", "adventure": "travel",
        "education": "education", "learning": "education",
        "how-to": "education", "guide": "education",
        "quotes": "quotes", "inspiration": "quotes",
        "motivation": "quotes", "mindset": "quotes",
        "health": "listicle", "fitness": "listicle",
        "tips": "listicle", "list": "listicle",
        "design": "modern", "creative": "modern",
        "lifestyle": "magazine", "culture": "magazine",
        "product": "product", "ecommerce": "product",
    }

    @classmethod
    def select_template(cls, topic: str, niche: str) -> str:
        """Auto-select the best template based on topic and niche."""
        t = topic.lower().strip()
        n = niche.lower().strip()

        # Check niche mapping first
        for key, template in cls.NICHE_TEMPLATE_MAP.items():
            if key in t or key in n:
                return template

        # Check template best_for
        for name, data in cls.TEMPLATES.items():
            if any(kw in t or kw in n for kw in data["best_for"]):
                return name

        return "modern"  # default fallback

    @classmethod
    def get_template_info(cls, template_name: str) -> dict:
        """Get template metadata."""
        return cls.TEMPLATES.get(template_name, cls.TEMPLATES["modern"])

    @classmethod
    def generate_spec(cls, template_name: str, content: ContentSpec,
                       brand_color: str = "#2563EB") -> DesignSpec:
        """Generate a complete DesignSpec from a template + content."""
        template = cls.TEMPLATES.get(template_name, cls.TEMPLATES["modern"])

        # Build colors based on template
        if template_name == "luxury":
            colors = ColorPalette(
                primary="#D4AF37", secondary="#1A1A2E", accent="#C0A030",
                background="#FFFFFF", text="#1A1A2E", text_light="#666666",
                surface="#F8F8F8", gradient_start="#D4AF37", gradient_end="#8B7530",
            )
        elif template_name == "technology":
            colors = ColorPalette(
                primary="#2563EB", secondary="#0F172A", accent="#3B82F6",
                background="#0F172A", text="#FFFFFF", text_light="#94A3B8",
                surface="#1E293B", gradient_start="#2563EB", gradient_end="#7C3AED",
            )
        elif template_name == "glassmorphism":
            colors = ColorPalette(
                primary="#8B5CF6", secondary="#1E1B4B", accent="#6D28D9",
                background="#1E1B4B", text="#FFFFFF", text_light="#A78BFA",
                surface="#2E1065", gradient_start="#8B5CF6", gradient_end="#3B82F6",
            )
        elif template_name == "luxury":
            colors = ColorPalette(
                primary="#D4AF37", secondary="#1A1A2E", accent="#C0A030",
                background="#FFFFFF", text="#1A1A2E", text_light="#666666",
                surface="#F8F8F8", gradient_start="#D4AF37", gradient_end="#8B7530",
            )
        elif template_name in ("travel", "hero"):
            colors = ColorPalette(
                primary="#0EA5E9", secondary="#0F172A", accent="#0284C7",
                background="#FFFFFF", text="#0F172A", text_light="#64748B",
                surface="#F0F9FF", gradient_start="#0EA5E9", gradient_end="#8B5CF6",
            )
        elif template_name in ("recipe", "food"):
            colors = ColorPalette(
                primary="#F97316", secondary="#1A1A2E", accent="#EA580C",
                background="#FFFFFF", text="#1A1A2E", text_light="#78716C",
                surface="#FFF7ED", gradient_start="#F97316", gradient_end="#E94560",
            )
        elif template_name == "quotes":
            colors = ColorPalette(
                primary="#8B5CF6", secondary="#1A1A2E", accent="#A78BFA",
                background="#FFFFFF", text="#1A1A2E", text_light="#6B7280",
                surface="#F5F3FF", gradient_start="#8B5CF6", gradient_end="#EC4899",
            )
        elif template_name in ("education", "infographic"):
            colors = ColorPalette(
                primary="#059669", secondary="#064E3B", accent="#10B981",
                background="#FFFFFF", text="#064E3B", text_light="#6B7280",
                surface="#ECFDF5", gradient_start="#059669", gradient_end="#3B82F6",
            )
        else:
            # Use brand color
            colors = ColorPalette(
                primary=brand_color, secondary="#1A1A2E", accent="#3B82F6",
                background="#FFFFFF", text="#1A1A2E", text_light="#6B7280",
                surface="#F8FAFC", gradient_start=brand_color, gradient_end="#8B5CF6",
            )

        # Set background type
        bg_type = template["background"]

        # Set layout
        layout_type = template["layout"]

        # Calculate typography based on template
        headline_size = 52
        if template_name in ("quotes", "hero"):
            headline_size = 60
        elif template_name in ("infographic", "education"):
            headline_size = 42

        spec = DesignSpec(
            content=content,
            colors=colors,
            typography=TypographySpec(
                headline_size_px=headline_size,
                headline_color=colors.text,
                headline_alignment="center" if layout_type == "centered" else "left",
                body_color=colors.text_light,
                cta_background=colors.primary,
                cta_color=colors.background,
            ),
            layout=LayoutSpec(
                layout_type=layout_type,
            ),
            background=BackgroundSpec(
                background_type=bg_type,
                gradient_colors=[colors.gradient_start or colors.primary,
                                 colors.gradient_end or colors.accent],
            ),
            icon=IconSpec(
                icon_category=cls._icon_for_template(template_name),
            ),
            template_name=template_name,
            design_rationale=template["vibe"],
        )

        return spec

    @staticmethod
    def _icon_for_template(template_name: str) -> str:
        """Map template to icon category."""
        icon_map = {
            "technology": "technology", "education": "education",
            "recipe": "food", "travel": "travel", "fashion": "fashion",
            "business": "business", "quotes": "motivation",
            "infographic": "marketing", "product": "business",
            "listicle": "education", "luxury": "fashion",
            "modern": "technology", "glassmorphism": "ai",
            "magazine": "lifestyle", "hero": "marketing",
            "comparison": "business", "split": "technology",
        }
        return icon_map.get(template_name, "business")