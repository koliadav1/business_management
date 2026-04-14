from fastapi_users import InvalidPasswordException
from sqladmin import ModelView
from sqladmin.filters import (
    BooleanFilter,
    ForeignKeyFilter,
    StaticValuesFilter,
)
from fastapi_users.password import PasswordHelper
from wtforms import PasswordField, ValidationError

from src.models.teams import Team
from src.models.users import User
from src.utils.password_validation import password_validate

password_helper = PasswordHelper()


class UserAdmin(ModelView, model=User):
    column_list = [
        User.id,
        User.email,
        User.role,
        User.team,
        User.created_at,
        User.is_active,
        User.is_superuser,
    ]
    column_labels = {User.hashed_password: "Password"}
    form_excluded_columns = [
        User.team_id,
        User.created_at,
        User.updated_at,
        User.id,
    ]
    form_overrides = {"hashed_password": PasswordField}
    column_searchable_list = [User.email, "team.name"]
    column_filters = [
        StaticValuesFilter(
            User.role,
            [
                ("USER", "User"),
                ("ADMIN", "Admin"),
                ("MANAGER", "Manager"),
                ("EMPLOYEE", "Employee"),
            ],
            title="Role",
        ),
        BooleanFilter(User.is_active),
        BooleanFilter(User.is_superuser),
        ForeignKeyFilter(User.team_id, Team.name, title="Team"),
    ]

    async def on_model_change(
        self, data: dict, model: User, is_created: bool, request
    ) -> None:
        raw_password = data.get("hashed_password")
        email = data.get("email") or getattr(model, "email", None)

        if raw_password:
            try:
                password_validate(raw_password, email)
            except InvalidPasswordException as e:
                raise ValidationError(
                    f"Password verification failed: {e.reason}"
                )
            data.update(hashed_password=password_helper.hash(raw_password))
