"""
Pinterest AI Content Engine — FastAPI Application
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Bootstrap the project root onto sys.path so `packages.*` (e.g. graphic_engine)
# resolves both in Docker (packages mounted at /packages) and local uvicorn runs.
def _find_project_root():
    d = Path(__file__).resolve().parent
    for _ in range(6):
        if (d / "packages").is_dir():
            return d
        d = d.parent
    return None

PROJECT_ROOT = _find_project_root()
if PROJECT_ROOT is not None and str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables and seed demo content on startup.

    Resilient: if the database is unreachable the API still boots so
    DB-free endpoints (e.g. the demo agent workflow) keep working.
    """
    try:
        from app.core.seed import seed_demo_data
        from app.core.database import async_session_factory

        async with async_session_factory() as session:
            await seed_demo_data(session)
    except Exception as e:
        import logging

        logging.getLogger("uvicorn.error").warning(
            "Database unavailable at startup — API running without persistence: %s", e
        )
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered Pinterest content creation studio with multi-agent orchestration",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.app_version}