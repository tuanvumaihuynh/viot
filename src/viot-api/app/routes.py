from fastapi import APIRouter

from app.modules.auth.api import auth_router, user_router
from app.modules.team.api import router as org_router

router = APIRouter()


router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(user_router, prefix="/users", tags=["User"])
router.include_router(org_router, prefix="/teams", tags=["Teams"])
