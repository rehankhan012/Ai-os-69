"""
Pinterest integration endpoints.

OAuth flow (popup-based, no auth on the callback URL):
1. GET  /pinterest/auth-url     (authenticated) -> returns consent URL + state token.
       The state token is stored in a Setting row: "pinterest_oauth_state:<state>" -> user_id
2. GET  /pinterest/callback     (NO auth) -> Pinterest redirects here with ?code=&state=.
       We look up user_id from the state token, exchange the code for tokens,
       store them, then redirect to the dashboard /settings?pinterest=connected
3. GET  /pinterest/status       (authenticated) -> connection status + account info
4. POST /pinterest/disconnect   (authenticated) -> remove credentials
5. GET  /pinterest/boards       (authenticated) -> list real boards
6. POST /pinterest/boards       (authenticated) -> create a board
7. POST /pinterest/pins         (authenticated) -> publish a real pin
8. GET  /pinterest/analytics    (authenticated) -> account analytics
"""

import base64
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.setting import Setting
from app.models.pin import Pin
from app.services.pinterest_service import pinterest_service
from packages.pinterest import PinterestAuthError, PinterestAPIError

router = APIRouter()

FRONTEND_REDIRECT = "http://localhost:3000/settings"


class CreateBoardRequest(BaseModel):
    name: str
    description: str = ""
    privacy: str = "PUBLIC"


class PublishPinRequest(BaseModel):
    board_id: str
    title: str
    description: str = ""
    link: str = ""
    alt_text: str = ""
    image_path: str = ""
    image_content_type: str = "image/png"
    # base64-encoded image data (data:image/png;base64,... or raw base64)
    image_base64: str = ""
    # reference a stored graphic — uses its png_path if available, else renders SVG
    graphic_id: str = ""


def _state_setting_key(state: str) -> str:
    return f"pinterest_oauth_state:{state}"


async def _store_state(db: AsyncSession, state: str, user_id) -> None:
    db.add(Setting(
        user_id=user_id,
        key=_state_setting_key(state),
        value="1",
        category="pinterest",
    ))


async def _resolve_state_user(db: AsyncSession, state: str) -> User | None:
    """Find the user that owns a state token. Clean it up after use."""
    result = await db.execute(
        select(Setting).where(Setting.key == _state_setting_key(state))
    )
    s = result.scalar_one_or_none()
    if not s:
        return None
    user_id = s.user_id
    await db.delete(s)
    return user_id


def _check_configured() -> None:
    if not settings.pinterest_client_id or not settings.pinterest_client_secret:
        raise HTTPException(
            status_code=503,
            detail="Pinterest is not configured. Add PINTEREST_CLIENT_ID and PINTEREST_CLIENT_SECRET to .env (create a free app at developers.pinterest.com).",
        )


@router.get("/auth-url")
async def get_auth_url(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the Pinterest OAuth consent URL. Frontend opens it in a new tab."""
    _check_configured()

    state = secrets.token_urlsafe(32)
    await _store_state(db, state, user.id)
    await db.flush()

    scopes = [s.strip() for s in settings.pinterest_scopes.split(",") if s.strip()]
    url = (
        f"https://www.pinterest.com/oauth/?client_id={settings.pinterest_client_id}"
        f"&redirect_uri={settings.pinterest_redirect_uri}"
        f"&response_type=code&scope={','.join(scopes)}&state={state}"
    )
    return {"authorization_url": url, "state": state, "redirect_uri": settings.pinterest_redirect_uri}


@router.get("/callback")
async def oauth_callback(
    code: str = Query(""),
    state: str = Query(""),
    db: AsyncSession = Depends(get_db),
):
    """Pinterest redirects here (NO auth header) after user consent.

    The state token identifies the platform user. Exchange the code for tokens,
    store them securely, then bounce to the dashboard.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    user_id = await _resolve_state_user(db, state)
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state — try connecting again")

    try:
        await pinterest_service.store_oauth_tokens(db, user_id, code, settings.pinterest_redirect_uri)
        await pinterest_service.get_connection_status(db, user_id)
    except (PinterestAuthError, PinterestAPIError) as e:
        raise HTTPException(status_code=400, detail=f"Pinterest authorization failed: {e}")

    return RedirectResponse(f"{FRONTEND_REDIRECT}?pinterest=connected", status_code=303)


@router.get("/status")
async def get_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Connection status + cached account info."""
    return await pinterest_service.get_connection_status(db, user)


@router.post("/disconnect")
async def disconnect(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove stored Pinterest credentials."""
    await pinterest_service.disconnect(db, user)
    return {"connected": False}


@router.get("/boards")
async def list_boards(
    force: bool = False,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List real Pinterest boards (cached; refresh with ?force=true)."""
    _check_configured()
    try:
        boards = await pinterest_service.list_boards(db, user, force=force)
        return {"boards": boards, "count": len(boards)}
    except PinterestAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except PinterestAPIError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.post("/boards")
async def create_board(
    body: CreateBoardRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a real Pinterest board."""
    _check_configured()
    if not body.name.strip():
        raise HTTPException(status_code=400, detail="Board name is required")
    try:
        board = await pinterest_service.create_board(db, user, body.name, body.description, body.privacy)
        return {"success": True, "board": board}
    except PinterestAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except PinterestAPIError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


@router.post("/pins")
async def publish_pin(
    body: PublishPinRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Publish a real pin to the connected Pinterest account."""
    _check_configured()
    if not body.board_id:
        raise HTTPException(status_code=400, detail="board_id is required")
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Pin title is required")

    image_path = body.image_path or ""
    image_content_type = body.image_content_type or "image/png"

    # Resolve image bytes from: base64 > graphic record > image_path
    image_bytes = None
    if body.image_base64:
        b64 = body.image_base64.split(",", 1)[-1] if "," in body.image_base64 else body.image_base64
        try:
            image_bytes = base64.b64decode(b64)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image_base64 payload")
    elif body.graphic_id:
        from app.models.graphic import Graphic

        result = await db.execute(
            select(Graphic).where(Graphic.id == body.graphic_id, Graphic.user_id == user.id)
        )
        graphic = result.scalar_one_or_none()
        if graphic and graphic.png_path:
            image_path = graphic.png_path
        elif graphic and graphic.svg_content:
            image_bytes = _rasterize_svg(graphic.svg_content, graphic.width, graphic.height)
            if image_bytes is None:
                raise HTTPException(
                    status_code=400,
                    detail="Graphic is SVG-only and server-side rasterization is unavailable — export PNG from the Graphic Studio and upload it, or send image_base64.",
                )
        else:
            raise HTTPException(status_code=404, detail="Graphic not found or has no image data")

    if image_bytes is None and not image_path:
        raise HTTPException(
            status_code=400,
            detail="Provide image_base64, a graphic_id with a rasterized image, or an image_path.",
        )

    try:
        pin = await pinterest_service.publish_pin(
            db=db,
            user=user,
            board_id=body.board_id,
            title=body.title,
            description=body.description,
            image_bytes=image_bytes,
            image_path=image_path or None,
            image_content_type=image_content_type,
            link=body.link,
            alt_text=body.alt_text,
        )
    except PinterestAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except PinterestAPIError as e:
        raise HTTPException(status_code=e.status, detail=str(e))

    # Mark a local pin as published if one matches the title
    result = await db.execute(
        select(Pin).where(Pin.user_id == user.id, Pin.title == body.title).order_by(Pin.created_at.desc())
    )
    local_pin = result.scalars().first()
    if local_pin:
        local_pin.status = "published"
        local_pin.published_at = datetime.now(timezone.utc)

    return {"success": True, "pin": pin}


@router.get("/analytics")
async def get_analytics(
    start_date: str = Query(...),
    end_date: str = Query(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Account analytics between two dates (YYYY-MM-DD)."""
    _check_configured()
    try:
        data = await pinterest_service.get_analytics(db, user, start_date, end_date)
        return {"success": True, "start_date": start_date, "end_date": end_date, "data": data}
    except PinterestAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except PinterestAPIError as e:
        raise HTTPException(status_code=e.status, detail=str(e))


def _rasterize_svg(svg: str, width: int = 1000, height: int = 1500) -> bytes | None:
    """Rasterize SVG to PNG bytes. Uses cairosvg if available, else svglib+Pillow."""
    try:
        import cairosvg

        return cairosvg.svg2png(bytestring=svg.encode(), output_width=width, output_height=height)
    except Exception:
        pass
    try:
        import io

        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM

        drawing = svg2rlg(io.StringIO(svg))
        if drawing is None:
            return None
        drawing.width, drawing.height = width, height
        buf = io.BytesIO()
        renderPM.drawToFile(drawing, buf, fmt="PNG", dpi=72)
        return buf.getvalue()
    except Exception:
        return None
