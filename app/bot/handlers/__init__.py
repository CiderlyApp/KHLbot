from .common import router as common_router
from .matches import router as matches_router
from .preferences import router as preferences_router
from .fallback import router as fallback_router

__all__ = ["common_router", "matches_router", "preferences_router", "fallback_router"]
