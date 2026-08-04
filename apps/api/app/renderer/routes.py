"""
Graphic Rendering Engine API endpoints.

Provides:
- POST /api/v1/renderer/design — Get AI design spec for a topic
- POST /api/v1/renderer/render — Render a design spec to SVG
- GET /api/v1/renderer/templates — List all available templates
- POST /api/v1/renderer/preview — Generate a preview image
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel

from packages.graphic_engine.src.ai_design.agent import AIDesignAgent
from packages.graphic_engine.src.engine.renderer import GraphicRenderer
from packages.graphic_engine.src.templates.engine import TemplateEngine

router = APIRouter()
design_agent = AIDesignAgent()
renderer = GraphicRenderer()
template_engine = TemplateEngine()


class DesignRequest(BaseModel):
    topic: str
    audience: str = ""
    mood: str = "clean"
    niche: str = ""
    brand_color: str = "#2563EB"
    brand_profile: str = "default"
    variations: int = 3


class RenderRequest(BaseModel):
    topic: str
    variation: str = "A"
    audience: str = ""
    mood: str = "clean"
    niche: str = ""
    brand_color: str = "#2563EB"
    brand_profile: str = "default"


@router.post("/design")
async def get_design(
    body: DesignRequest,
):
    """Get AI-generated design specifications for a topic."""
    result = await design_agent.design(
        topic=body.topic,
        audience=body.audience,
        mood=body.mood,
        niche=body.niche,
        brand_color=body.brand_color,
        brand_profile=body.brand_profile,
        count=body.variations,
    )
    return {
        "success": True,
        "template_selected": result["template_selected"],
        "template_rationale": result["template_rationale"],
        "design_rationale": result["design_rationale"],
        "variations": result["variations"],
        "best_variation": result["best_variation"],
    }


@router.post("/render")
async def render_design(
    body: RenderRequest,
):
    """Render a design spec to a complete SVG graphic."""
    # Get the design spec
    result = await design_agent.design(
        topic=body.topic,
        audience=body.audience,
        mood=body.mood,
        niche=body.niche,
        brand_color=body.brand_color,
        brand_profile=body.brand_profile,
        count=3,
    )

    # Find the requested variation
    target_var = body.variation.upper()
    var_data = None
    for v in result["variations"]:
        if v["variation"] == target_var:
            var_data = v
            break

    if not var_data:
        var_data = result["variations"][0]

    # Build a DesignSpec from the data
    from packages.graphic_engine.src.engine.spec import (
        DesignSpec, ContentSpec, ColorPalette, TypographySpec,
        LayoutSpec, BackgroundSpec, IconSpec, BrandingSpec
    )

    spec = DesignSpec(
        content=ContentSpec(
            headline=var_data["content"]["headline"],
            subheadline=var_data["content"]["subheadline"],
            body_text=var_data["content"]["body"],
            cta=var_data["content"]["cta"],
            list_items=var_data["content"]["list_items"],
        ),
        colors=ColorPalette(
            primary=var_data["colors"]["primary"],
            secondary=var_data["colors"]["secondary"],
            accent=var_data["colors"]["accent"],
            background=var_data["colors"]["background"],
            text=var_data["colors"]["text"],
            gradient_start=var_data["colors"].get("gradient_start", ""),
            gradient_end=var_data["colors"].get("gradient_end", ""),
        ),
        typography=TypographySpec(
            headline_font=var_data["typography"]["headline_font"],
            headline_size_px=var_data["typography"]["headline_size_px"],
            headline_weight=var_data["typography"]["headline_weight"],
            headline_color=var_data["typography"]["headline_color"],
            headline_alignment=var_data["typography"]["headline_alignment"],
            body_font=var_data["typography"]["body_font"],
            body_size_px=var_data["typography"]["body_size_px"],
            readability_score=var_data["typography"]["readability_score"],
        ),
        layout=LayoutSpec(
            width=var_data["layout"]["width"],
            height=var_data["layout"]["height"],
            layout_type=var_data["layout"]["type"],
        ),
        background=BackgroundSpec(
            background_type=var_data["background"]["type"],
            gradient_colors=var_data["background"]["gradient_colors"],
        ),
        icon=IconSpec(icon_category=""),
        branding=BrandingSpec(
            footer_text=var_data["branding"]["footer_text"],
            social_handle=var_data["branding"]["social_handle"],
            show_footer=var_data["branding"]["show_footer"],
        ),
        template_name=var_data.get("template", "modern"),
        variation_name=var_data["variation"],
        quality_score=var_data["quality_score"],
    )

    # Render the SVG
    svg = renderer.render(spec)

    return HTMLResponse(
        content=svg,
        media_type="image/svg+xml",
        headers={
            "X-Design-Template": spec.template_name,
            "X-Design-Variation": spec.variation_name,
            "X-Quality-Score": str(spec.quality_score),
        },
    )


@router.get("/templates")
async def list_templates():
    """List all available templates with metadata."""
    templates = []
    for name, data in TemplateEngine.TEMPLATES.items():
        templates.append({
            "id": name,
            "name": data["name"],
            "vibe": data["vibe"],
            "background": data["background"],
            "layout": data["layout"],
            "best_for": data["best_for"],
        })
    return {"templates": templates, "total": len(templates)}


@router.post("/preview")
async def generate_preview(
    body: DesignRequest,
):
    """Generate an embeddable HTML preview of all design variations."""
    result = await design_agent.design(
        topic=body.topic,
        audience=body.audience,
        mood=body.mood,
        niche=body.niche,
        brand_color=body.brand_color,
        brand_profile=body.brand_profile,
        count=body.variations,
    )

    # Generate SVG for each variation
    previews = []
    for var_data in result["variations"]:
        from packages.graphic_engine.src.engine.spec import (
            DesignSpec, ContentSpec, ColorPalette, TypographySpec,
            LayoutSpec, BackgroundSpec, IconSpec, BrandingSpec
        )
        spec = DesignSpec(
            content=ContentSpec(headline=var_data["content"]["headline"], cta=var_data["content"]["cta"]),
            colors=ColorPalette(
                primary=var_data["colors"]["primary"],
                secondary=var_data["colors"]["secondary"],
                accent=var_data["colors"]["accent"],
                background=var_data["colors"]["background"],
                text=var_data["colors"]["text"],
            ),
            typography=TypographySpec(
                headline_font=var_data["typography"]["headline_font"],
                headline_size_px=var_data["typography"]["headline_size_px"],
                headline_color=var_data["typography"]["headline_color"],
            ),
            layout=LayoutSpec(layout_type=var_data["layout"]["type"]),
            background=BackgroundSpec(
                background_type=var_data["background"]["type"],
                gradient_colors=var_data["background"]["gradient_colors"],
            ),
            template_name=var_data.get("template", "modern"),
            variation_name=var_data["variation"],
            quality_score=var_data["quality_score"],
        )
        svg = renderer.render(spec)
        previews.append({
            "variation": var_data["variation"],
            "quality_score": var_data["quality_score"],
            "svg": svg,
        })

    return {
        "success": True,
        "topic": body.topic,
        "template": result["template_selected"],
        "rationale": result["design_rationale"],
        "previews": previews,
    }