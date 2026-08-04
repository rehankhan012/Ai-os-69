"""
Vercel Python serverless entrypoint for the AI Content OS API.

Mangum adapts the FastAPI ASGI app to Vercel's serverless invocation. The
function lives at api/index.py, so Vercel routes /api/* to it natively; the
original path is preserved through the request event.
"""

import os
import sys

# api/index.py lives at <root>/api/index.py; the monorepo content is bundled
# at <root>/ (includeFiles globs are relative to the project root).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(REPO_ROOT, "apps", "api")

for path in (API_DIR, REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from app.main import app  # noqa: E402


# Ensure tables + demo content exist on cold start (serverless has no guaranteed
# lifespan event, so seed explicitly — the seeder is idempotent).
def _seed_on_startup() -> None:
    try:
        import asyncio

        from app.core.database import async_session_factory
        from app.core.seed import seed_demo_data

        async def _run():
            async with async_session_factory() as session:
                await seed_demo_data(session)

        asyncio.run(_run())
    except Exception:
        # Non-fatal: API still boots; endpoints will surface DB issues normally.
        pass


_seed_on_startup()

from mangum import Mangum  # noqa: E402

handler = Mangum(app, lifespan="off")
