from .auth import router as auth_router
from .comments import router as comments_router
from .evaluations import router as evaluations_router
from .meetings import router as meetings_router
from .tasks import router as tasks_router
from .teams import router as teams_router
from .users import router as users_router

__all__ = [
    "users_router",
    "teams_router",
    "tasks_router",
    "meetings_router",
    "evaluations_router",
    "comments_router",
    "auth_router",
]
