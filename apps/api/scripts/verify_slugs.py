import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import async_session_factory
from app.services.workflow_service import WorkflowService
from app.models.article import Article
from sqlalchemy import select

async def main():
    service = WorkflowService()
    user_id = "00000000-0000-0000-0000-000000000001" # Assuming a mock user id or we can query one
    
    async with async_session_factory() as db:
        # get a valid user if possible, otherwise rely on constraint (or maybe no fk constraint for testing)
        from app.models.user import User
        user = await db.execute(select(User).limit(1))
        user = user.scalar_one_or_none()
        
        if not user:
            print("No user found in DB to attach the generated articles to. Aborting verification.")
            return

        user_id = str(user.id)
        print(f"Using user_id: {user_id}")

        print("\nGenerating Article 1: '10 Ways to Earn Money Online in 2026'")
        res1 = await service.run_full_workflow(db, user_id=user_id, topic="10 Ways to Earn Money Online in 2026", niche="Business")
        print(f"Article 1 generated. Success: {res1['success']}")
        
        print("\nGenerating Article 2: '10 Ways to Earn Money Online in 2026'")
        res2 = await service.run_full_workflow(db, user_id=user_id, topic="10 Ways to Earn Money Online in 2026", niche="Business")
        print(f"Article 2 generated. Success: {res2['success']}")

        print("\nGenerating Article 3: '10 Ways to Earn Money Online in 2026'")
        res3 = await service.run_full_workflow(db, user_id=user_id, topic="10 Ways to Earn Money Online in 2026", niche="Business")
        print(f"Article 3 generated. Success: {res3['success']}")
        
        # Verify from database
        result = await db.execute(
            select(Article.title, Article.slug).where(
                Article.title.like("%10 Ways to Earn Money Online in 2026%")
            ).order_by(Article.created_at.desc()).limit(3)
        )
        articles = result.all()
        print("\n--- Verification of Slugs in Database ---")
        for a in articles:
            print(f"Title: {a.title} | Slug: {a.slug}")
            
if __name__ == "__main__":
    asyncio.run(main())
