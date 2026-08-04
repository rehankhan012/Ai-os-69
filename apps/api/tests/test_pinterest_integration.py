"""Test the Pinterest API client and integration flow with a mocked Pinterest API."""

import asyncio
import base64
import sys
from pathlib import Path


def _find_project_root():
    d = Path(__file__).resolve().parent
    for _ in range(6):
        if (d / "packages").is_dir():
            return d
        d = d.parent
    return None


ROOT = _find_project_root()
API_DIR = Path(__file__).resolve().parent.parent
for p in (API_DIR, ROOT):
    if p is not None and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from packages.pinterest import PinterestClient, PinterestAuthError  # noqa: E402


def _mock_oauth_token(request):
    body = request.content.decode()
    if "grant_type=authorization_code" in body:
        return {
            "access_token": "mock-access-token",
            "refresh_token": "mock-refresh-token",
            "token_type": "bearer",
            "expires_in": 7200,
        }
    if "grant_type=refresh_token" in body:
        return {
            "access_token": "mock-refreshed-access-token",
            "refresh_token": "mock-refresh-token",
            "token_type": "bearer",
            "expires_in": 7200,
        }
    raise AssertionError(f"Unknown token request: {body}")


async def test_oauth_and_publish():
    import httpx

    # Mock transport: handle /oauth/token, /media, upload_url, /pins
    upload_params = {"key": "uploads/x", "policy": "p", "signature": "s"}

    def handler(request: httpx.Request) -> httpx.Response:
        url = request.url.path
        if url == "/v5/oauth/token":
            return httpx.Response(200, json=_mock_oauth_token(request))
        if url == "/v5/media":
            return httpx.Response(200, json={
                "media_id": "media-123",
                "upload_url": "https://upload.example.com/upload",
                "upload_parameters": upload_params,
            })
        if url == "/v5/pins" and request.method == "POST":
            return httpx.Response(200, json={
                "id": "pin-456",
                "board_id": "board-1",
                "title": "Test Pin",
                "description": "Test description",
                "link": "https://example.com",
                "created_at": "2026-01-01T00:00:00Z",
            })
        if url == "/upload":
            return httpx.Response(200, text="ok")
        if url == "/v5/boards":
            return httpx.Response(200, json={
                "items": [
                    {"id": "board-1", "name": "Tech Tips", "description": "", "privacy": "PUBLIC", "pin_count": 5, "url": "https://pinterest.com/board-1"},
                    {"id": "board-2", "name": "Marketing", "description": "", "privacy": "PUBLIC", "pin_count": 3, "url": "https://pinterest.com/board-2"},
                ],
                "bookmark": None,
            })
        if url == "/v5/user_account":
            return httpx.Response(200, json={
                "username": "testuser",
                "full_name": "Test User",
                "board_count": 2,
                "pin_count": 8,
                "follower_count": 150,
            })
        raise AssertionError(f"Unhandled request: {request.method} {url}")

    transport = httpx.MockTransport(handler)

    p = PinterestClient(
        client_id="test-id",
        client_secret="test-secret",
        api_base="https://api.pinterest.com/v5",
        transport=transport,
    )

    # 1. OAuth code exchange
    token = await p.exchange_code("the-code", "http://localhost:8000/api/v1/pinterest/callback")
    assert token["access_token"] == "mock-access-token"
    assert p.access_token == "mock-access-token"
    print("1. OAuth code exchange: OK")

    # 2. Refresh
    refreshed = await p.refresh_access_token("mock-refresh-token")
    assert refreshed["access_token"] == "mock-refreshed-access-token"
    print("2. Token refresh: OK")

    # 3. User account
    acct = await p.get_user_account()
    assert acct["username"] == "testuser"
    print("3. User account: OK")

    # 4. Boards
    boards = await p.list_boards()
    assert len(boards["items"]) == 2
    print("4. List boards: OK")

    # 5. Full publish pipeline (register media -> upload -> create pin)
    pin = await p.publish_image_pin(
        board_id="board-1",
        title="Test Pin",
        description="Test description",
        image_bytes=b"\x89PNG fake image data",
        content_type="image/png",
        link="https://example.com",
    )
    assert pin["id"] == "pin-456"
    print("5. Full publish pipeline (media + pin): OK")

    # 6. Auth error handling
    p2 = PinterestClient(client_id="x", client_secret="y")
    try:
        await p2.get_user_account()
        raise AssertionError("Should have raised auth error")
    except PinterestAuthError:
        print("6. Auth error handling: OK")

    print("\nALL PINTEREST CLIENT TESTS PASSED")


asyncio.run(test_oauth_and_publish())
