import asyncio
import os
import sys
from pathlib import Path

# Add project root to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.core.database import async_session_factory
from app.core.seed import seed_demo_data

async def _run():
    print("Creating tables and seeding demo data in Neon...")
    async with async_session_factory() as session:
        await seed_demo_data(session)
    print("Done!")

asyncio.run(_run())
