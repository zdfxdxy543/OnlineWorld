from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.forum import router as forum_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.netdisk import router as netdisk_router
from app.api.v1.endpoints.world import router as world_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(world_router, prefix="/world", tags=["world"])
api_router.include_router(forum_router, prefix="/forum", tags=["forum"])
api_router.include_router(netdisk_router, prefix="/netdisk", tags=["netdisk"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
