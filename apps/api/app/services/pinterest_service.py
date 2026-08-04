"""
Pinterest integration service.

Bridges the Pinterest API v5 client with the platform's data model:
- Stores OAuth tokens per-user (encrypted at rest in the Settings table)
- Reports connection status + account info
- Publishes real pins from the publishing queue / pin drafts
- Manages boards

Security: tokens are encrypted at rest using the app SECRET_KEY.
"""

import base64
import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.setting import Setting
from app.models.user import User
from packages.pinterest import PinterestClient, PinterestAuthError, PinterestAPIError

logger = logging.getLogger(__name__)

# Setting keys (stored per-user)
K_ACCESS_TOKEN = "pinterest_access_token"
K_REFRESH_TOKEN = "pinterest_refresh_token"
K_TOKEN_EXPIRY = "pinterest_token_expires_at"
K_ACCOUNT = "pinterest_account"
K_CONNECTED = "pinterest_connected"
K_BOARDS_CACHE = "pinterest_boards_cache"


def _fernet() -> Fernet:
    """Derive a stable Fernet key from the app secret."""
    digest = hashlib.sha256(settings.secret_key.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def _encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def _decrypt(value: str) -> str:
    try:
        return _fernet().decrypt(value.encode()).decode()
    except InvalidToken:
        # Fall back to plaintext (pre-encryption values) for graceful upgrades
        return value


class PinterestService:
    """High-level Pinterest operations tied to the platform models."""

    def __init__(self):
        self._client: Optional[PinterestClient] = None

    # ------------------------------------------------------------------
    # Token storage
    # ------------------------------------------------------------------

    async def _get_setting(self, db: AsyncSession, user_id, key: str) -> Optional[str]:
        result = await db.execute(
            select(Setting).where(Setting.user_id == user_id, Setting.key == key)
        )
        s = result.scalar_one_or_none()
        return s.value if s else None

    async def _set_setting(self, db: AsyncSession, user_id, key: str, value: str) -> None:
        result = await db.execute(
            select(Setting).where(Setting.user_id == user_id, Setting.key == key)
        )
        s = result.scalar_one_or_none()
        if s:
            s.value = value
        else:
            db.add(Setting(user_id=user_id, key=key, value=value, category="pinterest"))

    # ------------------------------------------------------------------
    # Client construction
    # ------------------------------------------------------------------

    async def get_client(self, db: AsyncSession, user: User | object) -> PinterestClient:
        """Build an authenticated client for the user, refreshing if needed.

        Accepts a User model or a raw user_id (uuid or string) for OAuth callbacks.
        """
        user_id = getattr(user, "id", user)
        token_enc = await self._get_setting(db, user_id, K_ACCESS_TOKEN)
        if not token_enc:
            raise PinterestAuthError("No Pinterest account connected")

        client = PinterestClient(
            client_id=settings.pinterest_client_id,
            client_secret=settings.pinterest_client_secret,
            access_token=_decrypt(token_enc),
            api_base=settings.pinterest_api_base,
            oauth_base=settings.pinterest_oauth_base,
        )

        # Refresh if expired (tokens typically live ~2h in dev mode)
        expiry_str = await self._get_setting(db, user_id, K_TOKEN_EXPIRY)
        if expiry_str:
            try:
                expiry = datetime.fromisoformat(expiry_str)
                if datetime.now(timezone.utc) >= expiry:
                    await self.refresh_tokens(db, user_id, client)
            except ValueError:
                pass
        return client

    async def refresh_tokens(self, db: AsyncSession, user: User | object, client: PinterestClient) -> None:
        """Refresh access + refresh tokens and persist them."""
        user_id = getattr(user, "id", user)
        refresh_enc = await self._get_setting(db, user_id, K_REFRESH_TOKEN)
        if not refresh_enc:
            raise PinterestAuthError("No refresh token available — reconnect the account")
        token = await client.refresh_access_token(_decrypt(refresh_enc))
        await self._persist_tokens(db, user_id, token)

    async def _persist_tokens(self, db: AsyncSession, user: User | object, token: dict[str, Any]) -> None:
        user_id = getattr(user, "id", user)
        access = token.get("access_token", "")
        refresh = token.get("refresh_token", "")
        if access:
            await self._set_setting(db, user_id, K_ACCESS_TOKEN, _encrypt(access))
        if refresh:
            await self._set_setting(db, user_id, K_REFRESH_TOKEN, _encrypt(refresh))
        if token.get("expires_in"):
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(token["expires_in"]))
            await self._set_setting(db, user_id, K_TOKEN_EXPIRY, expires_at.isoformat())
        await self._set_setting(db, user_id, K_CONNECTED, "true")
        await db.flush()

    # ------------------------------------------------------------------
    # OAuth flow
    # ------------------------------------------------------------------

    async def store_oauth_tokens(self, db: AsyncSession, user: User | object, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange an OAuth code for tokens and store them."""
        user_id = getattr(user, "id", user)
        client = PinterestClient(
            client_id=settings.pinterest_client_id,
            client_secret=settings.pinterest_client_secret,
            api_base=settings.pinterest_api_base,
            oauth_base=settings.pinterest_oauth_base,
        )
        token = await client.exchange_code(code, redirect_uri)
        await self._persist_tokens(db, user_id, token)
        return token

    # ------------------------------------------------------------------
    # Connection status
    # ------------------------------------------------------------------

    async def get_connection_status(self, db: AsyncSession, user: User | object) -> dict[str, Any]:
        user_id = getattr(user, "id", user)
        connected = await self._get_setting(db, user_id, K_CONNECTED) == "true"
        account: dict[str, Any] = {}
        if connected:
            try:
                client = await self.get_client(db, user_id)
                account = await client.get_user_account()
                account = {
                    "username": account.get("username"),
                    "full_name": account.get("full_name"),
                    "about": account.get("about"),
                    "board_count": account.get("board_count"),
                    "pin_count": account.get("pin_count"),
                    "follower_count": account.get("follower_count"),
                    "profile_image_url": account.get("profile_image", {}).get("60x60", ""),
                }
                await self._set_setting(db, user_id, K_ACCOUNT, json.dumps(account))
            except (PinterestAuthError, PinterestAPIError) as e:
                logger.warning("Pinterest status check failed: %s", e)
                connected = False
        return {
            "connected": connected,
            "account": account,
            # Lets the dashboard show a friendly setup notice without probing auth-url
            "configured": bool(settings.pinterest_client_id and settings.pinterest_client_secret),
        }

    async def disconnect(self, db: AsyncSession, user: User) -> None:
        """Remove all stored Pinterest credentials."""
        for key in (K_ACCESS_TOKEN, K_REFRESH_TOKEN, K_TOKEN_EXPIRY, K_ACCOUNT, K_CONNECTED, K_BOARDS_CACHE):
            result = await db.execute(
                select(Setting).where(Setting.user_id == user.id, Setting.key == key)
            )
            s = result.scalar_one_or_none()
            if s:
                await db.delete(s)

    # ------------------------------------------------------------------
    # Boards
    # ------------------------------------------------------------------

    async def list_boards(self, db: AsyncSession, user: User, force: bool = False) -> list[dict[str, Any]]:
        client = await self.get_client(db, user)
        data = await client.list_boards()
        items = data.get("items", [])
        boards = [
            {
                "id": b.get("id"),
                "name": b.get("name"),
                "description": b.get("description"),
                "privacy": b.get("privacy"),
                "pin_count": b.get("pin_count"),
                "url": b.get("url"),
            }
            for b in items
        ]
        await self._set_setting(db, user.id, K_BOARDS_CACHE, json.dumps(boards))
        return boards

    async def create_board(self, db: AsyncSession, user: User, name: str, description: str = "", privacy: str = "PUBLIC") -> dict[str, Any]:
        client = await self.get_client(db, user)
        board = await client.create_board(name=name, description=description, privacy=privacy)
        return {
            "id": board.get("id"),
            "name": board.get("name"),
            "description": board.get("description"),
            "privacy": board.get("privacy"),
        }

    # ------------------------------------------------------------------
    # Publish a pin
    # ------------------------------------------------------------------

    async def publish_pin(
        self,
        db: AsyncSession,
        user: User,
        board_id: str,
        title: str,
        description: str = "",
        image_bytes: Optional[bytes] = None,
        image_path: Optional[str] = None,
        image_content_type: str = "image/png",
        link: str = "",
        alt_text: str = "",
    ) -> dict[str, Any]:
        """Publish a real pin to Pinterest. Requires image bytes or a local file path."""
        if image_bytes is None:
            if not image_path:
                raise PinterestAPIError(0, "No image provided for the pin")
            with open(image_path, "rb") as f:
                image_bytes = f.read()

        client = await self.get_client(db, user)
        pin = await client.publish_image_pin(
            board_id=board_id,
            title=title,
            description=description,
            image_bytes=image_bytes,
            content_type=image_content_type,
            link=link,
            alt_text=alt_text,
        )
        return {
            "id": pin.get("id"),
            "board_id": pin.get("board_id"),
            "title": pin.get("title"),
            "description": pin.get("description"),
            "link": pin.get("link"),
            "url": pin.get("link"),
            "created_at": pin.get("created_at"),
        }

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    async def get_analytics(
        self,
        db: AsyncSession,
        user: User,
        start_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        client = await self.get_client(db, user)
        return await client.get_account_analytics(start_date=start_date, end_date=end_date)


pinterest_service = PinterestService()
