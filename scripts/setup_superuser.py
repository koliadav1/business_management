import asyncio
import traceback
from contextlib import asynccontextmanager

from fastapi_users import exceptions
from fastapi_users.db import SQLAlchemyUserDatabase

from src.models.users import User
from src.schemas.users import UserCreate
from src.core.database import session_maker
from src.core.config import settings
from src.services.user_manager import UserManager


@asynccontextmanager
async def get_user_manager():
    async with session_maker() as session:
        user_db = SQLAlchemyUserDatabase(session, User)
        yield UserManager(user_db)


async def create_first_superuser():
    email = settings.SUPER_USER_EMAIL
    password = settings.SUPER_USER_PASSWORD

    if not email or not password:
        print(
            "SUPER_USER_PASSWORD или SUPER_USER_EMAIL не заданы для суперпользователя"
        )
        return

    async with get_user_manager() as user_manager:
        try:
            user = await user_manager.get_by_email(email)
            if user:
                print("Суперпользователь уже существует")
                return
        except exceptions.UserNotExists:
            pass
        except Exception as e:
            print(f"Ошибка: {e}")
            traceback.print_exc()
            return
        try:
            await user_manager.create(
                UserCreate(
                    email=email,
                    password=password,
                    is_superuser=True,
                    is_active=True,
                    is_verified=True,
                ),
                safe=False,
            )
            print("Суперпользователь создан")
        except Exception as e:
            print(f"Ошибка: {e}")
            traceback.print_exc()
            return


if __name__ == "__main__":
    asyncio.run(create_first_superuser())
