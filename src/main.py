from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager

from fastapi.security import HTTPBearer

from src.core.exceptions import register_exception_handlers
from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.core.database import engine
from src.utils.dependencies import fastapi_users
from src.api import (
    tasks_router,
    teams_router,
    evaluations_router,
    meetings_router,
    auth_router,
    users_router,
    comments_router,
)
from src.admin import setup_admin

http_bearer = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    description="Система упрравления бизнесом",
    lifespan=lifespan,
    dependencies=[Depends(http_bearer)],
)
setup_admin(app)
register_exception_handlers(app)

app.include_router(teams_router)
app.include_router(tasks_router)
app.include_router(comments_router)
app.include_router(evaluations_router)
app.include_router(meetings_router)

app.include_router(auth_router)
app.include_router(users_router)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
