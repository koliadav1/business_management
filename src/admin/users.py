from sqladmin import ModelView
from fastapi_users.password import PasswordHelper

from src.models.users import User

password_helper = PasswordHelper()


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.role,
        User.team,
        User.created_at,
        User.is_superuser,
    ]
    column_labels = {User.hashed_password: "Password"}
    form_include_pk = True
    form_excluded_columns = [
        User.team_id,
        User.created_at,
        User.updated_at,
        User.id,
    ]

    async def on_model_change(
        self, data: dict, model: User, is_created: bool, request
    ) -> None:
        raw_password = (
            data.get("hashed_password") or password_helper.generate()
        )
        if is_created or model.hashed_password != raw_password:
            data.update(hashed_password=password_helper.hash(raw_password))
