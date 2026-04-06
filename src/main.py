from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    BearerTransport,
    AuthenticationBackend,
    JWTStrategy,
)

from src.schemas.users import UserCreate, UserRead, UserUpdate
from src.models.users import User
from src.core.database import engine
from src.core.config import settings
from src.utils.dependencies import get_user_manager

bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt", transport=bearer_transport, get_strategy=get_jwt_strategy
)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager=get_user_manager, auth_backends=[auth_backend]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(description="Система упрравления бизнесом", lifespan=lifespan)


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
