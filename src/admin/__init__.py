from sqladmin import Admin
from fastapi import FastAPI

from src.core.database import session_maker
from .teams import TeamAdmin
from .tasks import TaskAdmin
from .users import UserAdmin


def setup_admin(app: FastAPI):
    admin = Admin(app=app, session_maker=session_maker, title="Админ-панель")

    admin.add_view(UserAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(TeamAdmin)

    # return admin
