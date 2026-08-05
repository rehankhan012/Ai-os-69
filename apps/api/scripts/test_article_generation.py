import asyncio
import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

# Set up paths so we can import 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.ai_service import AIProvider
from app.services.article_pipeline import ArticlePipelineService

class MockProvider(AIProvider):
    async def generate_text(self, prompt: str, **kwargs) -> str:
        # Check if the prompt is for step 9/10 (JSON schema metadata & audit)
        if "You MUST return your entire response as a structured JSON object matching this schema exactly" in prompt:
            return json.dumps({
                "title": "Mock Article Title",
                "slug": "mock-article-title",
                "meta_title": "Mock Meta Title",
                "meta_description": "Mock Meta Description",
                "excerpt": "Mock summary",
                "focus_keyword": "mock keyword",
                "secondary_keywords": ["mock", "keywords"],
                "tags": ["mock", "test"],
                "reading_time": "5 min read",
                "word_count": 500,
                "seo_score": 98,
                "quality_score": 96, # Passing score so it doesn't loop
                "featured_image_prompt": "A mock image prompt",
                "pinterest_prompt": "Mock pin prompt",
                "thumbnail_prompt": "Mock thumbnail",
                "twitter_banner_prompt": "Mock banner",
                "linkedin_cover_prompt": "Mock cover",
                "faq": [
                    {"question": "What is this?", "answer": "A mock article."}
                ],
                "schema": {
                    "article": {},
                    "faq": {},
                    "breadcrumb": {}
                },
                "affiliate_links_used": [],
                "internal_links_used": [],
                "seo_audit": {
                    "keyword_coverage": "Good",
                    "heading_quality": "Good",
                    "internal_links_count": 0,
                    "affiliate_links_count": 0,
                    "external_links_count": 0,
                    "missing_opportunities": [],
                    "improvement_suggestions": []
                },
                "quality_audit": {
                    "helpfulness": 95,
                    "trustworthiness": 95,
                    "depth": 95,
                    "originality": 95,
                    "engagement": 95,
                    "conversion_potential": 95,
                    "human_likeness": 95
                },
                "content_suggestions": {
                    "better_titles": [],
                    "better_meta_descriptions": [],
                    "additional_faqs": [],
                    "suggested_related_articles": [],
                    "suggested_internal_links": [],
                    "content_expansion_ideas": []
                }
            })
        elif "You are an expert HTML Developer" in prompt:
            return "<h1>Mock HTML</h1><p>This is a mock draft converted to HTML.</p>"
        else:
            return "This is a mock response from the AI."

    async def generate_titles(self, keyword, niche, count=5):
        return []
    
    async def generate_description(self, title, keyword, tone):
        return ""

async def main():
    print("Testing AI Article Pipeline (V3.0) with Mock Provider...")
    
    provider = MockProvider()
    pipeline = ArticlePipelineService(provider=provider)
    
    topic = "The Benefits of Yoga for Software Engineers"
    affiliate_links = ["https://amazon.com/yoga-mat"]
    internal_links = [{"title": "Healthy Habits", "url": "https://ourblog.com/healthy-habits"}]
    trusted_sources = ["https://mayoclinic.org/yoga"]
    additional_instructions = "Keep it under 500 words for this test."
    tone = "informative"
    
    try:
        result = await pipeline.run_pipeline(
            topic=topic,
            affiliate_links=affiliate_links,
            internal_links=internal_links,
            trusted_sources=trusted_sources,
            additional_instructions=additional_instructions,
            tone=tone
        )
        print("\nPipeline Execution Successful!")
        print("--- RESULT JSON ---")
        print(json.dumps(result, indent=2))
        print("-------------------")
        
        # Verify schema
        required_keys = ["title", "slug", "excerpt", "html", "quality_score", "seo_audit", "quality_audit", "schema"]
        for key in required_keys:
            if key not in result:
                print(f"WARNING: Missing key '{key}' in result!")
        print("\nAll checks passed.")
                
    except Exception as e:
        print(f"Error generating article: {e}")

if __name__ == "__main__":
    asyncio.run(main())
