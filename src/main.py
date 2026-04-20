# TODO валидацию данных на уровне pydantic и exceptionhandlers

from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.core.database import engine
from src.utils.dependencies import auth_backend, fastapi_users
from src.api.tasks import router as tasks_router
from src.api.teams import router as teams_router
from src.api.evaluations import router as evaluations_router
from src.admin import setup_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(description="Система упрравления бизнесом", lifespan=lifespan)
setup_admin(app)

app.include_router(tasks_router)
app.include_router(teams_router)
app.include_router(evaluations_router)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["auth"]
)
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
