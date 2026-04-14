from types import SimpleNamespace

from fastapi_users.db import SQLAlchemyUserDatabase
from sqladmin.authentication import AuthenticationBackend

from src.services.user_manager import UserManager
from src.models.users import User
from src.core.database import session_maker


class SQLAdminAuth(AuthenticationBackend):
    async def login(self, request):
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        async with session_maker() as session:
            user_db = SQLAlchemyUserDatabase(session, User)
            user_manager = UserManager(user_db)

            user = await user_manager.authenticate(
                credentials=SimpleNamespace(username=email, password=password)
            )

            if user and user.is_superuser:
                request.session.update({"token": "authenticated"})
                return True
        return False

    async def logout(self, request):
        request.session.clear()
        return True

    async def authenticate(self, request):
        return "token" in request.session
