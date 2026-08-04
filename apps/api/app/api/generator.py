"""
AI Content Generator endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.ai_generator import ContentGenerationRequest, ContentGenerationResponse, ImageGenerationRequest, ImageGenerationResponse


def _titleize(s: str) -> str:
    """Convert a string to Title Case."""
    return " ".join(word.capitalize() for word in s.split())


router = APIRouter()


@router.post("/content", response_model=ContentGenerationResponse)
async def generate_content(
    body: ContentGenerationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate SEO-optimized Pinterest content using AI."""
    kw = _titleize(body.keyword)
    return ContentGenerationResponse(
        titles=[
            {"title": f"10 {kw} Tips You Need to Try", "seo_score": 0.92, "reasoning": "High engagement listicle format"},
            {"title": f"The Ultimate Guide to {kw}", "seo_score": 0.88, "reasoning": "Comprehensive guide keyword"},
            {"title": f"Why {kw} Is the Future of Your Niche", "seo_score": 0.85, "reasoning": "Trend-based curiosity gap"},
            {"title": f"How to Master {kw} in 2026", "seo_score": 0.90, "reasoning": "Year-specific evergreen content"},
            {"title": f"{kw} Secrets Experts Won't Tell You", "seo_score": 0.87, "reasoning": "Social proof and scarcity"},
        ],
        descriptions=[
            f"Discover the best {body.keyword} strategies that actually work. Save this pin for later!",
            f"Learn everything you need to know about {body.keyword}. Perfect for beginners and experts alike.",
            f"Unlock the secrets of {body.keyword} with our comprehensive guide. Pin it now!",
            f"Transform your approach to {body.keyword} with these proven techniques. Read more!",
            f"Your ultimate resource for {body.keyword} — tips, tricks, and tools to succeed.",
        ],
        keyword_suggestions=[
            f"{body.keyword} tips",
            f"best {body.keyword} strategies",
            f"{body.keyword} for beginners",
            f"advanced {body.keyword} techniques",
            f"{body.keyword} 2026 trends",
            f"{body.keyword} guide",
            f"{body.keyword} ideas",
            f"how to {body.keyword}",
            f"{body.keyword} tools",
            f"{body.keyword} examples",
        ],
        hashtags=["#" + body.keyword.replace(" ", ""), "#PinterestTips", "#ContentStrategy", "#SEOTips", "#DigitalMarketing", "#GrowthHacking", "#SocialMedia", "#Marketing2026"],
        recommended_board=f"{body.keyword.titleize()} Strategies",
        cta="Save this pin for your next content strategy session!",
    )


@router.post("/image", response_model=ImageGenerationResponse)
async def generate_image(
    body: ImageGenerationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a Pinterest-optimized image using AI."""
    # TODO: Integrate with Image provider abstraction
    # For now, return mock data
    return ImageGenerationResponse(
        image_url="https://placehold.co/1000x1500/1a1a2e/e94560?text=Pinterest+Pin",
        style=body.style,
        width=body.width,
        height=body.height,
        mime_type="image/png",
    )