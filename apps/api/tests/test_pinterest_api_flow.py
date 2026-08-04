"""End-to-end HTTP test of the Pinterest integration using SQLite + mocked Pinterest API."""

import asyncio
import sys
import uuid
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

import httpx  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core import database  # noqa: E402
from app.core.database import Base as REAL_BASE  # noqa: E402

# --- Switch to in-memory SQLite for this test ---
TEST_ENGINE = create_async_engine("sqlite+aiosqlite:///:memory:")
TEST_FACTORY = async_sessionmaker(TEST_ENGINE, class_=database.AsyncSession, expire_on_commit=False)

# Stable fake user across all requests in this test
FAKE_USER_ID = uuid.uuid4()


def _override_deps(fastapi_app):
    from app.core.database import get_db as real_get_db
    from app.api.auth import get_current_user

    async def fake_user():
        from app.models.user import User
        return User(id=FAKE_USER_ID, email="test@pinterest.io", username="testuser",
                    hashed_password="x", full_name="Test User")

    async def fake_db():
        async with TEST_FACTORY() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    fastapi_app.dependency_overrides[real_get_db] = fake_db
    fastapi_app.dependency_overrides[get_current_user] = fake_user

    return REAL_BASE.metadata


def main():
    import app.main as main_module
    from app.main import app as fastapi_app
    from fastapi.testclient import TestClient

    # Redirect the app's engine to the in-memory SQLite engine so startup
    # (create_all) and the real lifespan don't touch Postgres.
    main_module.engine = TEST_ENGINE
    main_module.Base = REAL_BASE
    database.engine = TEST_ENGINE
    database.async_session_factory = TEST_FACTORY

    metadata = _override_deps(fastapi_app)

    # Configure test env
    settings.pinterest_client_id = "test-id"
    settings.pinterest_client_secret = "test-secret"
    settings.pinterest_redirect_uri = "http://localhost:8000/api/v1/pinterest/callback"

    # Mock Pinterest transport
    def pin_handler(request: httpx.Request) -> httpx.Response:
        url = request.url.path
        if url == "/v5/oauth/token":
            return httpx.Response(200, json={
                "access_token": "mock-access",
                "refresh_token": "mock-refresh",
                "token_type": "bearer",
                "expires_in": 7200,
            })
        if url == "/v5/media":
            return httpx.Response(200, json={
                "media_id": "media-1",
                "upload_url": "https://upload.example.com/u",
                "upload_parameters": {"key": "k", "sig": "s"},
            })
        if url == "/v5/pins" and request.method == "POST":
            return httpx.Response(200, json={
                "id": "pin-live-1", "board_id": "board-1", "title": "Live Pin",
                "description": "desc", "created_at": "2026-01-01T00:00:00Z",
            })
        if url == "/u":
            return httpx.Response(200, text="ok")
        if url == "/v5/boards":
            return httpx.Response(200, json={"items": [
                {"id": "board-1", "name": "Tech Tips", "description": "", "privacy": "PUBLIC", "pin_count": 2, "url": "https://pinterest.com/b"},
            ], "bookmark": None})
        if url == "/v5/user_account":
            return httpx.Response(200, json={
                "username": "realuser", "full_name": "Real User", "board_count": 1, "pin_count": 2, "follower_count": 10,
            })
        raise AssertionError(f"Unhandled: {request.method} {url}")

    # Patch the client transport in the service
    from packages.pinterest import PinterestClient
    _orig_init = PinterestClient.__init__

    def _patched_init(self, *args, **kwargs):
        kwargs["transport"] = httpx.MockTransport(pin_handler)
        _orig_init(self, *args, **kwargs)

    PinterestClient.__init__ = _patched_init

    with TestClient(fastapi_app) as client:
        # Create tables
        asyncio.run(_create_tables(metadata))

        # 1. Auth URL
        r = client.get("/api/v1/pinterest/auth-url")
        assert r.status_code == 200, r.text
        auth_url = r.json()["authorization_url"]
        assert "pinterest.com/oauth" in auth_url
        print("1. GET /pinterest/auth-url -> OK")

        # Extract state from the URL
        import urllib.parse
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(auth_url).query)
        state = qs["state"][0]

        # 2. Callback (no auth header — uses state)
        r = client.get(f"/api/v1/pinterest/callback?code=test-code&state={state}", follow_redirects=False)
        assert r.status_code in (303, 307), r.text
        assert "/settings?pinterest=connected" in r.headers.get("location", "")
        print("2. GET /pinterest/callback -> OK (redirects to dashboard)")

        # 3. Status (authenticated)
        r = client.get("/api/v1/pinterest/status")
        assert r.status_code == 200, r.text
        status = r.json()
        assert status["connected"] is True, status
        assert status["account"]["username"] == "realuser", status
        print("3. GET /pinterest/status -> OK (connected as @realuser)")

        # 4. Boards
        r = client.get("/api/v1/pinterest/boards")
        assert r.status_code == 200, r.text
        boards = r.json()["boards"]
        assert len(boards) == 1 and boards[0]["name"] == "Tech Tips"
        print("4. GET /pinterest/boards -> OK")

        # 5. Publish a pin with base64 image
        import base64 as b64
        png = b64.b64encode(b"fake-png-bytes").decode()
        r = client.post("/api/v1/pinterest/pins", json={
            "board_id": "board-1",
            "title": "Live Pin",
            "description": "desc",
            "image_base64": f"data:image/png;base64,{png}",
        })
        assert r.status_code == 200, r.text
        assert r.json()["pin"]["id"] == "pin-live-1"
        print("5. POST /pinterest/pins -> OK (published live pin)")

        # 6. Disconnect
        r = client.post("/api/v1/pinterest/disconnect")
        assert r.status_code == 200
        r = client.get("/api/v1/pinterest/status")
        assert r.json()["connected"] is False
        print("6. POST /pinterest/disconnect -> OK")

        print("\nALL PINTEREST API FLOW TESTS PASSED")


async def _create_tables(metadata):
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(metadata.create_all)


if __name__ == "__main__":
    main()
