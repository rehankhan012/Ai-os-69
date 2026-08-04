"""
Demo content seeder.

Idempotent: only seeds when the database has no published articles, so it is
safe to run on every startup (local SQLite, Neon Postgres on Vercel, Docker).
Gives the public blog (Darkverse) immediate content out of the box.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.models.category import Category
from app.models.article import Article

logger = logging.getLogger(__name__)

DEMO_PASSWORD = "demo1234"

CATEGORIES = [
    {"name": "Technology", "slug": "technology", "color": "#3B82F6", "description": "AI, gadgets, and the digital future."},
    {"name": "Travel", "slug": "travel", "color": "#F59E0B", "description": "Budget trips, itineraries, and wanderlust."},
    {"name": "Wellness", "slug": "wellness", "color": "#10B981", "description": "Yoga, food, and everyday habits."},
]

ARTICLES = [
    {
        "title": "AI Marketing Strategies for Small Businesses",
        "slug": "ai-marketing-strategies-for-small-businesses",
        "category": "technology",
        "excerpt": "You don't need a huge budget or a data team to use AI in marketing. These are the strategies that actually move the needle for small businesses.",
        "content": """
<h2>Start with the boring work</h2>
<p>Before you deploy a single AI tool, get your foundations right. AI amplifies whatever you already have — if your customer data is a mess, a clever model won't fix it.</p>
<h2>Personalization without the headcount</h2>
<p>Segmented email flows, dynamic website copy, and tailored product recommendations used to require engineers. Today, a small business can personalize at scale with off-the-shelf tools.</p>
<h2>Content that compounds</h2>
<p>The biggest wins come from consistency. Use AI to draft, but always edit with a human voice. Repurpose one great piece into a dozen formats: a blog post becomes an email, a carousel, and three social captions.</p>
<h2>Measure what matters</h2>
<p>Track cost per acquisition, not impressions. Small teams win by being ruthless about which channels pay for themselves.</p>
<blockquote><p>AI doesn't replace your strategy — it removes the friction between your strategy and your customers.</p></blockquote>
""",
    },
    {
        "title": "Budget Travel Hacks for 2026",
        "slug": "budget-travel-hacks-for-2026",
        "category": "travel",
        "excerpt": "Flights, stays, and experiences cost less than you think — if you know the tricks. Here's how to travel well without blowing your savings.",
        "content": """
<h2>Book at the right time</h2>
<p>The sweet spot is roughly 6–8 weeks out for international flights. Set price alerts early and pounce on the dips.</p>
<h2>Stay where locals live</h2>
<p>Short-term rentals in residential neighborhoods cost a fraction of tourist-zone hotels — and you eat better, too.</p>
<h2>Eat like a local</h2>
<p>Street food and lunch specials are the secret to a great trip on a budget. Skip the restaurants with laminated menus and follow the queues.</p>
<h2>Transport on a budget</h2>
<p>Overnight buses and trains double as accommodation. Plan your sleeps around travel time and you'll save two ways at once.</p>
""",
    },
    {
        "title": "Vegan Meal Prep for Busy Weekdays",
        "slug": "vegan-meal-prep-for-busy-weekdays",
        "category": "wellness",
        "excerpt": "A Sunday afternoon of prep can carry you through the week. These plant-based recipes are fast, filling, and forgiving.",
        "content": """
<h2>The prep formula</h2>
<p>Pick one grain, one legume, one roasted vegetable tray, and one killer sauce. Mix and match all week without eating the same plate twice.</p>
<h2>Batch sauces are the cheat code</h2>
<p>A great tahini dressing or peanut sauce turns plain bowls into meals. Make a jar on Sunday and you're set.</p>
<h2>Storage that keeps crunch</h2>
<p>Store wet and dry separately. Nothing kills meal prep faster than soggy vegetables by Tuesday.</p>
<h2>Five-minute assembly</h2>
<p>Grain + legume + veg + sauce + seeds. That's the whole game. Each bowl takes about five minutes to assemble on a busy evening.</p>
""",
    },
    {
        "title": "The Best Coffee Brewing Methods at Home",
        "slug": "best-coffee-brewing-methods-at-home",
        "category": "wellness",
        "excerpt": "You don't need a barista setup to brew great coffee. Here's how to pick the method that fits your mornings.",
        "content": """
<h2>French press: the forgiving classic</h2>
<p>Coarse grind, four minutes, done. The French press is the easiest way to get rich, full-bodied coffee with almost no equipment.</p>
<h2>Pour-over: clarity in a cup</h2>
<p>If you want bright, tea-like clarity, a gooseneck kettle and a V60 reward you with the cleanest cup at home.</p>
<h2>Aeropress: the travel hero</h2>
<p>Fast, durable, and nearly impossible to mess up. It's the best companion for offices and trips.</p>
<h2>Grind fresh, always</h2>
<p>Whatever method you choose, grind right before brewing. Pre-ground coffee is the single biggest upgrade you'll ever make.</p>
""",
    },
    {
        "title": "Morning Yoga Routines for Beginners",
        "slug": "morning-yoga-routines-for-beginners",
        "category": "wellness",
        "excerpt": "Ten minutes of movement can change your whole day. This gentle routine is designed for absolute beginners.",
        "content": """
<h2>Why mornings work</h2>
<p>A short morning practice sets your posture, mood, and focus for the day. You don't need flexibility — you need consistency.</p>
<h2>The 10-minute routine</h2>
<p>Start with a few rounds of cat-cow, move through downward dog, and finish with a forward fold and child's pose. Breathe slowly throughout.</p>
<h2>Listen to your body</h2>
<p>Every body is different. If a pose pinches, back off and breathe. The goal is to feel better, not to hit a perfect shape.</p>
<h2>Build the habit</h2>
<p>Stack your practice onto an existing habit — right after brushing your teeth works surprisingly well.</p>
""",
    },
    {
        "title": "10 Best Coffee Brewing Ways",
        "slug": "10-best-coffee-brewing-ways",
        "category": "wellness",
        "excerpt": "From espresso to cold brew, here are the ten most popular ways to brew coffee and exactly who each one is for.",
        "content": """
<h2>Espresso and moka pot</h2>
<p>For the bold: espresso machines and moka pots deliver concentrated, syrupy shots. Perfect for milk drinks.</p>
<h2>Drip and batch brew</h2>
<p>Set-and-forget convenience for busy households. A good drip machine with fresh grounds beats a bad pour-over every time.</p>
<h2>Cold brew</h2>
<p>Steep coarse grounds for 12–18 hours for a smooth, low-acid concentrate that shines over ice.</p>
<h2>Find your style</h2>
<p>There's no wrong answer — only the method you'll actually use on a Tuesday morning.</p>
""",
    },
]


async def seed_demo_data(db: AsyncSession) -> None:
    """Create tables if missing and seed demo content when empty. Idempotent."""
    from app.core.database import Base, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Only seed when nothing is published yet.
    count = await db.execute(
        select(func.count(Article.id)).where(Article.status == "published")
    )
    if (count.scalar() or 0) > 0:
        return

    # Demo user
    result = await db.execute(select(User).where(User.email == "demo@example.com"))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            email="demo@example.com",
            username="demo",
            hashed_password=hash_password(DEMO_PASSWORD),
            full_name="Demo User",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.flush()

    # Categories
    categories = {}
    for c in CATEGORIES:
        result = await db.execute(select(Category).where(Category.slug == c["slug"]))
        cat = result.scalar_one_or_none()
        if cat is None:
            cat = Category(
                user_id=user.id,
                name=c["name"],
                slug=c["slug"],
                color=c["color"],
                description=c["description"],
            )
            db.add(cat)
            await db.flush()
        categories[c["slug"]] = cat

    # Articles (staggered publish dates, newest first)
    now = datetime.now(timezone.utc)
    for i, a in enumerate(ARTICLES):
        cat = categories[a["category"]]
        article = Article(
            user_id=user.id,
            title=a["title"],
            slug=a["slug"],
            excerpt=a["excerpt"],
            content=a["content"].strip(),
            category_id=cat.id,
            status="published",
            seo_score=80.0,
            ai_generated=False,
            published_at=now - timedelta(hours=3 * i + 1),
            view_count=0,
        )
        db.add(article)
        cat.article_count = (cat.article_count or 0) + 1

    try:
        await db.commit()
        logger.info(
            "Seeded demo content: 1 user, %d categories, %d published articles",
            len(CATEGORIES),
            len(ARTICLES),
        )
    except IntegrityError:
        # Concurrent cold starts may race the idempotency check — safe to ignore.
        await db.rollback()
        logger.info("Seed skipped — content already exists.")
