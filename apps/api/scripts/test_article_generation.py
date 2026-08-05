import asyncio
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Set up paths so we can import 'app'
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.services.ai_service import get_ai_provider

async def main():
    print("Testing AI Article Generation...")
    
    # We will use Gemini if available, or whatever is configured
    try:
        provider = get_ai_provider()
    except Exception as e:
        print(f"Error initializing provider: {e}")
        return
        
    print(f"Using provider: {type(provider).__name__}")
    
    topic = "The Benefits of Yoga for Software Engineers"
    affiliate_links = ["https://amazon.com/yoga-mat"]
    internal_links = [{"title": "Healthy Habits", "url": "https://ourblog.com/healthy-habits"}]
    trusted_sources = ["https://mayoclinic.org/yoga"]
    additional_instructions = "Keep it under 500 words for this test."
    tone = "informative"
    
    try:
        result = await provider.generate_article(
            topic=topic,
            affiliate_links=affiliate_links,
            internal_links=internal_links,
            trusted_sources=trusted_sources,
            additional_instructions=additional_instructions,
            tone=tone
        )
        print("\nGeneration Successful!")
        print("--- RESULT JSON ---")
        import json
        print(json.dumps(result, indent=2))
        print("-------------------")
        
        # Verify schema
        required_keys = ["title", "slug", "excerpt", "html"]
        for key in required_keys:
            if key not in result:
                print(f"WARNING: Missing key '{key}' in result!")
                
    except Exception as e:
        print(f"Error generating article: {e}")

if __name__ == "__main__":
    asyncio.run(main())
