from fastapi_users import InvalidPasswordException
from sqladmin import ModelView
from fastapi_users.password import PasswordHelper
from wtforms import PasswordField, ValidationError

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
    form_overrides = {"hashed_password": PasswordField}

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

        elif is_created:
            generated_password = password_helper.generate()
            try:
                password_validate(generated_password, email)
            except InvalidPasswordException as e:
                raise ValidationError(
                    f"Password verification failed: {e.reason}"
                )

            data.update(
                hashed_password=password_helper.hash(generated_password)
            )
