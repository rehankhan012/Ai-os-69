"""
Database engine and session factory.
"""

import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _async_url(url: str) -> str:
    """Normalize a Postgres URL for SQLAlchemy's async driver.

    Neon (Vercel integration) injects `postgres://...` connection strings;
    SQLAlchemy async needs `postgresql+asyncpg://`. The unpooled URL is
    preferred because asyncpg + Neon's pooled endpoint can hit prepared
    statement issues.

    asyncpg does not accept the `sslmode` query parameter (that's a
    libpq/psycopg2 concept) — it expects `ssl=require`. Rewrite it.
    """
    url = url.strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    else:
        return url

    # sslmode=require|prefer → ssl=require (asyncpg syntax)
    if "sslmode=require" in url:
        url = url.replace("sslmode=require", "ssl=require")
    elif "sslmode=prefer" in url:
        url = url.replace("sslmode=prefer", "ssl=require")
    return url


# Serverless (Vercel) runs each request in a fresh event loop — pooling would
# reuse connections bound to a dead loop ("another operation is in progress").
is_serverless = bool(os.environ.get("VERCEL"))

engine = create_async_engine(
    _async_url(settings.database_url_unpooled or settings.database_url),
    echo=settings.debug,
    poolclass=NullPool if is_serverless else None,
    pool_pre_ping=True,
)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncSession:
    """Yield an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
