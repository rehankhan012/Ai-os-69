from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.boards import router as boards_router
from app.api.pins import router as pins_router
from app.api.keywords import router as keywords_router
from app.api.analytics import router as analytics_router
from app.api.generator import router as generator_router
from app.api.settings import router as settings_router
from app.api.queue import router as queue_router
from app.api.images import router as images_router
from app.api.agents import router as agents_router
from app.renderer.routes import router as renderer_router
from app.api.articles import router as articles_router
from app.api.categories import router as categories_router
from app.api.media_library import router as media_router
from app.api.notifications import router as notifications_router
from app.api.revenue import router as revenue_router
from app.api.pinterest import router as pinterest_router
from app.api.workflow import router as workflow_router
from app.api.public import router as public_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(boards_router, prefix="/boards", tags=["Boards"])
router.include_router(pins_router, prefix="/pins", tags=["Pins"])
router.include_router(keywords_router, prefix="/keywords", tags=["Keywords"])
router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
router.include_router(generator_router, prefix="/generator", tags=["AI Generator"])
router.include_router(settings_router, prefix="/settings", tags=["Settings"])
router.include_router(queue_router, prefix="/queue", tags=["Queue"])
router.include_router(images_router, prefix="/images", tags=["Images"])
router.include_router(agents_router, prefix="/agents", tags=["AI Agents"])
router.include_router(renderer_router, prefix="/renderer", tags=["Graphic Renderer"])
router.include_router(articles_router, prefix="/articles", tags=["CMS Articles"])
router.include_router(categories_router, prefix="/cms", tags=["CMS Categories & Tags"])
router.include_router(media_router, prefix="/media", tags=["Media Library"])
router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
router.include_router(revenue_router, prefix="/revenue", tags=["Revenue"])
router.include_router(workflow_router, prefix="/workflow", tags=["Master Workflow"])
router.include_router(pinterest_router, prefix="/pinterest", tags=["Pinterest Integration"])
router.include_router(public_router, prefix="/public", tags=["Public Website"])