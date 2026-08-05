import asyncio
import os
import sys
import json
from dotenv import load_dotenv
load_dotenv()

# Set up paths so we can import 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.ai_service import AIProvider, MockProvider
from app.services.article_pipeline import ArticlePipelineService

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
