from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager

from fastapi.security import HTTPBearer

from src.core.exceptions import register_exception_handlers
from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.core.database import engine
from src.utils.dependencies import fastapi_users
from src.api.tasks import router as tasks_router
from src.api.teams import router as teams_router
from src.api.evaluations import router as evaluations_router
from src.api.meetings import router as meetings_router
from src.api.auth import router as auth_router
from src.api.users import router as user_router
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

app.include_router(tasks_router)
app.include_router(teams_router)
app.include_router(evaluations_router)
app.include_router(meetings_router)

app.include_router(auth_router)
app.include_router(user_router)

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
