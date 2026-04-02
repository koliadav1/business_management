from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(description="Система упрравления бизнесом", lifespan=lifespan)
