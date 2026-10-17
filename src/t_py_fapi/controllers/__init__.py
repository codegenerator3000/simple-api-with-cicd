from fastapi import APIRouter

from .city import router as city_router
from .market import router as market_router
from .street import router as street_router

router = APIRouter()
router.include_router(city_router)
router.include_router(street_router)
router.include_router(market_router)

__all__ = ["router"]
