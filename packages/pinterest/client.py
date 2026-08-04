"""
Pinterest API v5 client.

Official API docs: https://developers.pinterest.com/docs/api/v5/

Covers:
- OAuth 2.0 authorization URL + token exchange + refresh
- User account info
- Boards (list / create)
- Two-step media upload (register -> upload binary)
- Pins (create)
- Pin analytics

All methods return parsed JSON dicts. Errors raise PinterestAPIError with the
HTTP status and Pinterest error code/message.
"""

import base64
import logging
from typing import Any, Optional
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)


class PinterestAuthError(Exception):
    """Raised for OAuth/token errors (invalid code, expired token, etc.)."""


class PinterestAPIError(Exception):
    """Raised for non-2xx API responses."""

    def __init__(self, status: int, message: str, code: Optional[str] = None):
        self.status = status
        self.code = code
        super().__init__(f"Pinterest API error {status} ({code or 'unknown'}): {message}")


class PinterestClient:
    """Async client for the Pinterest API v5."""

    def __init__(
        self,
        client_id: str = "",
        client_secret: str = "",
        access_token: str = "",
        refresh_token: str = "",
        api_base: str = "https://api.pinterest.com/v5",
        oauth_base: str = "https://www.pinterest.com/oauth",
        timeout: float = 30.0,
        transport: Any = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.api_base = api_base.rstrip("/")
        self.oauth_base = oauth_base.rstrip("/")
        self.timeout = timeout
        # Optional httpx transport — used in tests to mock the API
        self._transport = transport

    # ------------------------------------------------------------------
    # OAuth 2.0
    # ------------------------------------------------------------------

    def build_authorization_url(
        self,
        redirect_uri: str,
        state: str,
        scopes: list[str] | None = None,
    ) -> str:
        """Build the Pinterest OAuth authorization URL (user-facing consent page)."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": ",".join(scopes or ["boards:read", "boards:write", "pins:read", "pins:write"]),
            "state": state,
        }
        return f"{self.oauth_base}/?{urlencode(params)}"

    async def exchange_code(self, code: str, redirect_uri: str) -> dict[str, Any]:
        """Exchange an authorization code for access + refresh tokens."""
        if not self.client_id or not self.client_secret:
            raise PinterestAuthError("Pinterest client_id/client_secret not configured")
        return await self._token_request(
            {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            }
        )

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh the access token using a refresh token."""
        if not self.client_id or not self.client_secret:
            raise PinterestAuthError("Pinterest client_id/client_secret not configured")
        return await self._token_request(
            {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        )

    async def _token_request(self, data: dict[str, str]) -> dict[str, Any]:
        basic = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        async with self._http() as client:
            resp = await client.post(
                f"{self.api_base}/oauth/token",
                headers={
                    "Authorization": f"Basic {basic}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data=data,
            )
        if resp.status_code >= 400:
            try:
                body = resp.json()
                message = body.get("message") or body.get("error_description") or resp.text
            except Exception:
                message = resp.text
            raise PinterestAuthError(f"Token request failed ({resp.status_code}): {message}")
        token = resp.json()
        self.access_token = token.get("access_token", self.access_token)
        self.refresh_token = token.get("refresh_token", self.refresh_token)
        return token

    # ------------------------------------------------------------------
    # Core request helper
    # ------------------------------------------------------------------

    def _http(self) -> httpx.AsyncClient:
        """Build the HTTP client, injecting a mock transport when provided."""
        return httpx.AsyncClient(timeout=self.timeout, transport=self._transport)

    async def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        if not self.access_token:
            raise PinterestAuthError("Not authenticated — connect a Pinterest account first")
        url = f"{self.api_base}{path}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        kwargs.setdefault("headers", headers)
        async with self._http() as client:
            resp = await client.request(method, url, **kwargs)
        if resp.status_code >= 400:
            try:
                body = resp.json()
                message = body.get("message") or resp.text
                code = body.get("code")
            except Exception:
                body = {}
                message = resp.text
                code = None
            # 401/403 with token issues -> surface as auth error so callers can refresh
            if resp.status_code in (401, 403) and "token" in message.lower():
                raise PinterestAuthError(f"Pinterest token invalid ({resp.status_code}): {message}")
            raise PinterestAPIError(resp.status_code, message, code)
        if resp.status_code == 204:
            return {}
        return resp.json()

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    async def get_user_account(self) -> dict[str, Any]:
        """Get the connected Pinterest user's account info."""
        return await self._request("GET", "/user_account")

    # ------------------------------------------------------------------
    # Boards
    # ------------------------------------------------------------------

    async def list_boards(self, page_size: int = 25, page_cursor: Optional[str] = None) -> dict[str, Any]:
        """List boards for the connected account."""
        params = {"page_size": page_size}
        if page_cursor:
            params["bookmark"] = page_cursor
        return await self._request("GET", f"/boards?{urlencode(params)}")

    async def get_board(self, board_id: str) -> dict[str, Any]:
        """Get a single board."""
        return await self._request("GET", f"/boards/{board_id}")

    async def create_board(
        self,
        name: str,
        description: str = "",
        privacy: str = "PUBLIC",
    ) -> dict[str, Any]:
        """Create a board. privacy: PUBLIC or SECRET."""
        return await self._request(
            "POST",
            "/boards",
            json={"name": name, "description": description, "privacy": privacy},
        )

    async def delete_board(self, board_id: str) -> None:
        """Delete a board."""
        await self._request("DELETE", f"/boards/{board_id}")

    # ------------------------------------------------------------------
    # Media upload (two-step)
    # ------------------------------------------------------------------

    async def register_media_upload(self) -> dict[str, Any]:
        """Step 1: register an image media upload, returns media_id + upload_url."""
        return await self._request("POST", "/media", json={"media_type": "image"})

    async def upload_media_file(
        self,
        upload_url: str,
        upload_parameters: dict[str, str],
        file_bytes: bytes,
        content_type: str = "image/png",
    ) -> None:
        """Step 2: upload binary data to the presigned upload_url (multipart form)."""
        async with self._http() as client:
            files = {"file": ("pin.png", file_bytes, content_type)}
            # upload_parameters is a flat key:value map sent as form fields
            resp = await client.post(upload_url, data=upload_parameters, files=files)
        if resp.status_code >= 400:
            raise PinterestAPIError(resp.status_code, f"Media upload failed: {resp.text[:300]}")

    # ------------------------------------------------------------------
    # Pins
    # ------------------------------------------------------------------

    async def create_pin(
        self,
        board_id: str,
        title: str,
        description: str = "",
        link: str = "",
        media_id: Optional[str] = None,
        alt_text: str = "",
    ) -> dict[str, Any]:
        """Create a pin from a registered media_id (image upload)."""
        media_source: dict[str, Any] = {"source_type": "image_url"}
        if media_id:
            media_source = {"source_type": "image_id", "media_id": media_id}

        payload: dict[str, Any] = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "media_source": media_source,
        }
        if link:
            payload["link"] = link
        if alt_text:
            payload["alt_text"] = alt_text
        return await self._request("POST", "/pins", json=payload)

    async def get_pin(self, pin_id: str) -> dict[str, Any]:
        """Get a single pin."""
        return await self._request("GET", f"/pins/{pin_id}")

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    async def get_pin_analytics(
        self,
        pin_id: str,
        start_date: str,
        end_date: str,
        metric_types: str = "IMPRESSION,SAVE,OUTBOUND_CLICK,PIN_CLICK",
    ) -> dict[str, Any]:
        """Get metrics for a pin between two dates (YYYY-MM-DD)."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "metric_types": metric_types,
        }
        return await self._request("GET", f"/pins/{pin_id}/analytics?{urlencode(params)}")

    async def get_account_analytics(
        self,
        start_date: str,
        end_date: str,
        metric_types: str = "IMPRESSION,SAVE,OUTBOUND_CLICK,PIN_CLICK",
    ) -> dict[str, Any]:
        """Get account-level analytics between two dates (YYYY-MM-DD)."""
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "metric_types": metric_types,
        }
        return await self._request("GET", f"/user_account/analytics?{urlencode(params)}")

    # ------------------------------------------------------------------
    # Convenience: full publish pipeline
    # ------------------------------------------------------------------

    async def publish_image_pin(
        self,
        board_id: str,
        title: str,
        description: str,
        image_bytes: bytes,
        content_type: str = "image/png",
        link: str = "",
        alt_text: str = "",
    ) -> dict[str, Any]:
        """Upload an image and create a pin from it in one call."""
        # Step 1: register
        media = await self.register_media_upload()
        upload_url = media.get("upload_url")
        upload_params = media.get("upload_parameters") or {}
        media_id = media.get("media_id")
        if not upload_url or not media_id:
            raise PinterestAPIError(0, "Pinterest media registration returned no upload_url/media_id")

        # Step 2: upload binary
        await self.upload_media_file(upload_url, upload_params, image_bytes, content_type)

        # Step 3: create pin
        return await self.create_pin(
            board_id=board_id,
            title=title,
            description=description,
            link=link,
            media_id=media_id,
            alt_text=alt_text,
        )
