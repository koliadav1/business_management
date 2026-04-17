from fastapi_users import InvalidPasswordException


def password_validate(
    password: str,
    email: str,
):
    if len(password) < 8:
        raise InvalidPasswordException(
            reason="Пароль должен быть не короче 8 символов"
        )
    if len(password) > 100:
        raise InvalidPasswordException(
            reason="Пароль должен быть не длинее 100 символов"
        )
    if email in password:
        raise InvalidPasswordException(
            reason="Пароль не должен содержать адрес почты"
        )
    if not any(ch.isdigit() for ch in password):
        raise InvalidPasswordException(
            reason="Пароль должен содержать хотя бы одну цифру"
        )
