from typing import Tuple

from fastapi_users import BaseUserManager, exceptions, models
from fastapi_users import jwt
from fastapi_users.authentication import JWTStrategy
from fastapi_users.jwt import SecretType, decode_jwt, generate_jwt


class JWTRefreshStrategy(JWTStrategy):
    refresh_token_header = "X-Refresh-Token"

    def __init__(
        self,
        secret: SecretType,
        lifetime_seconds: int,
        refresh_lifetime_seconds: int,
        token_audience: list[str] = ["fastapi-users:auth"],
        algorithm: str = "HS256",
        public_key: SecretType | None = None,
    ):
        super().__init__(
            secret, lifetime_seconds, token_audience, algorithm, public_key
        )
        self.refresh_lifetime_seconds = refresh_lifetime_seconds

    async def write_token(
        self, user: models.UP, token_type: str = "access"
    ) -> str:
        data = {
            "sub": str(user.id),
            "aud": self.token_audience,
            "type": token_type,
        }

        lifetime = (
            self.lifetime_seconds
            if token_type == "access"
            else self.refresh_lifetime_seconds
        )
        return generate_jwt(
            data,
            self.encode_key,
            lifetime,
            algorithm=self.algorithm,
        )

    async def read_token(
        self,
        token: str | None,
        user_manager: BaseUserManager[models.UP, models.ID],
        expected_type: str = "access",
    ) -> models.UP | None:
        if token is None:
            return None

        try:
            data = decode_jwt(
                token,
                self.decode_key,
                self.token_audience,
                algorithms=[self.algorithm],
            )

            token_type = data.get("type")
            if token_type != expected_type:
                return None

            user_id = data.get("sub")
            if user_id is None:
                return None
        except jwt.PyJWTError:
            return None

        try:
            parsed_id = user_manager.parse_id(user_id)
            return await user_manager.get(parsed_id)
        except (exceptions.UserNotExists, exceptions.InvalidID):
            return None

    async def generate_tokens(self, user: models.UP) -> Tuple[str, str]:
        access_token = await self.write_token(user, "access")
        refresh_token = await self.write_token(user, "refresh")
        return access_token, refresh_token

    async def refresh_access_token(
        self,
        refresh_token: str,
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> str | None:
        user = await self.read_token(refresh_token, user_manager, "refresh")

        if not user:
            return None

        return await self.write_token(user, "access")
