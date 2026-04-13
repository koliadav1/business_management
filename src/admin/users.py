from sqladmin import ModelView

from src.models.users import User


class UserAdmin(ModelView, model=User):
    pass
