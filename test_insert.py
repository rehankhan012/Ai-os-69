import asyncio
import asyncpg
from datetime import datetime

DATABASE_URL = "postgresql://neondb_owner:npg_2oxH1RDbWJCK@ep-spring-bird-axqxrk06-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

async def run():
    conn = await asyncpg.connect(DATABASE_URL)
    
    query = """
    INSERT INTO site_articles (
        id, title, slug, excerpt, content, featured_image_url, seo_score, 
        view_count, reading_time_minutes, published_at, category_name
    )
    VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11
    )
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        slug = EXCLUDED.slug,
        excerpt = EXCLUDED.excerpt,
        content = EXCLUDED.content,
        featured_image_url = EXCLUDED.featured_image_url,
        seo_score = EXCLUDED.seo_score,
        reading_time_minutes = EXCLUDED.reading_time_minutes,
        published_at = EXCLUDED.published_at,
        category_name = EXCLUDED.category_name;
    """
    
    try:
        res = await conn.execute(query, 
            "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11", "Test Publish", "test-publish", 
            "Excerpt", "Content", None, 95.5, 0, 5, datetime.utcnow(), "Technology"
        )
        print("Success:", res)
    except Exception as e:
        print("Error:", e)
    finally:
        await conn.close()

asyncio.run(run())
