"""
Application configuration via environment variables.
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "AI Content OS"
    app_version: str = "1.0.0"
    debug: bool = True
    secret_key: str = "change-this-to-a-secure-random-key"
    environment: str = "development"

    # Database
    # Defaults to a self-contained SQLite file so the API runs with zero external
    # services. Override with DATABASE_URL (e.g. via docker-compose) to use PostgreSQL.
    database_url: str = "sqlite+aiosqlite:///./pinterest_ai.db"
    database_sync_url: str = "sqlite:///./pinterest_ai.db"
    # Neon injects both a pooled and an unpooled URL; asyncpg prefers the unpooled one.
    database_url_unpooled: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = "change-this-to-a-secure-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # CORS — allow any https Vercel deployment of the blog, plus the custom domain
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "https://darkverseblog.vercel.app",
        "https://darkverse-rehans-projects-47f74bf3.vercel.app",
        "https://*.vercel.app",
    ]

    # Storage
    storage_backend: str = "local"
    storage_local_path: str = "./uploads"

    # Pinterest API (https://developers.pinterest.com)
    pinterest_client_id: str = ""
    pinterest_client_secret: str = ""
    # Must match exactly the redirect URI registered in the Pinterest developer app
    pinterest_redirect_uri: str = "http://localhost:8000/api/v1/pinterest/callback"
    pinterest_api_base: str = "https://api.pinterest.com/v5"
    pinterest_oauth_base: str = "https://www.pinterest.com/oauth"
    pinterest_scopes: str = "boards:read,boards:write,pins:read,pins:write,user_accounts:read"

    # Website publishing (pluggable — set SITE_PUBLISH_TYPE=wordpress and
    # provide a URL + token to push articles to an external site, e.g. darkverseblog.vercel.app)
    site_publish_url: str = ""
    site_publish_token: str = ""
    site_publish_type: str = ""  # "wordpress" | "generic" | "" (local-only)

    # Public website (darkverseblog.vercel.app) branding + deployment URL
    site_name: str = "Darkverse"
    site_tagline: str = "Ideas, stories, and deep dives"
    site_description: str = "Darkverse is a publication about ideas, technology, and the stories shaping the world."
    site_url: str = "http://localhost:3001"  # public site origin (prod: https://darkverseblog.vercel.app)

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()