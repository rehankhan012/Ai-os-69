from pydantic import BaseModel


class ContentGenerationRequest(BaseModel):
    keyword: str
    niche: str | None = None
    audience: str | None = None
    tone: str = "professional"
    goal: str = "engagement"
    count: int = 5


class ContentGenerationResponse(BaseModel):
    titles: list[dict] = []  # [{title, seo_score, reasoning}]
    descriptions: list[str] = []
    keyword_suggestions: list[str] = []
    hashtags: list[str] = []
    recommended_board: str | None = None
    cta: str | None = None


class ImageGenerationRequest(BaseModel):
    prompt: str
    style: str = "modern"
    width: int = 1000
    height: int = 1500
    include_logo: bool = False
    logo_url: str | None = None


class ImageGenerationResponse(BaseModel):
    image_url: str
    style: str
    width: int
    height: int
    mime_type: str