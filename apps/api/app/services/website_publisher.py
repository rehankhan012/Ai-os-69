"""
Website publisher — pushes articles to an external site.

Pluggable by design:
- SITE_PUBLISH_TYPE=wordpress  -> WordPress REST API (wp-json) create/post
- SITE_PUBLISH_TYPE=generic    -> generic POST to SITE_PUBLISH_URL with a JSON payload
- unset                         -> built-in mode: the public blog site (darkverse.co.in)
                                   is powered by this CMS, so published articles appear
                                   there automatically. No external push needed.

Configure via env (apps/api/.env):
    SITE_PUBLISH_URL=https://darkverse.co.in/wp-json/wp/v2
    SITE_PUBLISH_TOKEN=<application password or bearer token>
    SITE_PUBLISH_TYPE=wordpress
"""

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class WebsitePublisherError(Exception):
    """Raised when publishing to an external site fails."""


class WebsitePublisher:
    """Handles publishing articles to an external website."""

    @property
    def configured(self) -> bool:
        return bool(settings.site_publish_url and settings.site_publish_type)

    async def publish_article(self, article) -> dict:
        """Publish an article. Returns a status report dict."""
        if not self.configured:
            return {
                "status": "published",
                "site": "builtin",
                "url": f"{settings.site_url.rstrip('/')}/{article.slug or article.id.hex}",
                "message": "Live on your website — published articles appear automatically on your blog.",
            }

        publish_type = (settings.site_publish_type or "").lower()
        if publish_type == "wordpress":
            return await self._publish_wordpress(article)
        if publish_type == "generic":
            return await self._publish_generic(article)
        return {
            "status": "local_only",
            "message": f"Unknown SITE_PUBLISH_TYPE '{settings.site_publish_type}' — published locally only.",
        }

    async def _publish_wordpress(self, article) -> dict:
        """Create/update a post via the WordPress REST API."""
        base = settings.site_publish_url.rstrip("/")
        if not base.endswith("wp/v2"):
            base = base + "/wp-json/wp/v2" if "wp-json" not in base else base
        url = f"{base}/posts"
        headers = {"Authorization": f"Bearer {settings.site_publish_token}"}
        payload = {
            "title": article.title,
            "content": article.content or "",
            "excerpt": article.excerpt or "",
            "status": "publish",
            "slug": article.slug or None,
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as e:
            raise WebsitePublisherError(f"Website request failed: {e}")

        if resp.status_code >= 400:
            raise WebsitePublisherError(
                f"Website rejected the post ({resp.status_code}): {resp.text[:300]}"
            )
        data = resp.json()
        return {
            "status": "published",
            "site": settings.site_publish_url,
            "external_id": str(data.get("id", "")),
            "url": data.get("link", ""),
            "message": "Article published to your website.",
        }

    async def _publish_generic(self, article) -> dict:
        """Generic webhook-style publish: POST article JSON to SITE_PUBLISH_URL."""
        url = settings.site_publish_url.rstrip("/")
        headers = {}
        if settings.site_publish_token:
            headers["Authorization"] = f"Bearer {settings.site_publish_token}"
            
        # We need the category if possible, but website_publisher doesn't always have it loaded.
        # We'll just send the fields we have on the article object. The Vercel site can handle null categories.
        
        def _reading_time(content: str | None) -> int:
            if not content:
                return 1
            words = len(content.replace("<", " <").split())
            return max(1, round(words / 200))
            
        payload = {
            "id": str(article.id),
            "title": article.title,
            "slug": article.slug or article.id.hex,
            "excerpt": article.excerpt,
            "content": article.content,
            "featured_image_url": article.featured_image_url,
            "seo_score": getattr(article, "seo_score", 0.0),
            "view_count": getattr(article, "view_count", 0),
            "reading_time_minutes": _reading_time(article.content),
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "status": "published",
        }
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
        except httpx.HTTPError as e:
            raise WebsitePublisherError(f"Website request failed: {e}")

        if resp.status_code >= 400:
            raise WebsitePublisherError(
                f"Website rejected the post ({resp.status_code}): {resp.text[:300]}"
            )
        return {
            "status": "published",
            "site": settings.site_publish_url,
            "message": "Article published to your website.",
        }


website_publisher = WebsitePublisher()
