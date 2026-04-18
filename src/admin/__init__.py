from sqladmin import Admin
from fastapi import FastAPI

from src.core.database import session_maker
from src.core.config import settings
from .teams import TeamAdmin
from .tasks import TaskAdmin
from .users import UserAdmin
from .evaluations import EvaluationAdmin
from .meetings import MeetingAdmin
from .auth import SQLAdminAuth


def setup_admin(app: FastAPI):
    auth_backend = SQLAdminAuth(secret_key=settings.SECRET)
    admin = Admin(
        app=app,
        session_maker=session_maker,
        title="Админ-панель",
        authentication_backend=auth_backend,
    )

    admin.add_view(UserAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(EvaluationAdmin)
    admin.add_view(MeetingAdmin)
