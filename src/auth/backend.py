from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import AuthenticationBackend

from .strategy import JWTRefreshStrategy
from .token_transport import BearerRefreshTransport


class AuthenticationRefreshBackend(AuthenticationBackend):
    name: str
    transport: BearerRefreshTransport

    def __init__(self, name, transport, get_strategy):
        super().__init__(name, transport, get_strategy)

    async def login(
        self, strategy: JWTRefreshStrategy, user: models.UP
    ) -> Response:
        access, refresh = await strategy.generate_tokens(user)
        return await self.transport.get_login_response(access, refresh)

    async def refresh(
        self,
        refresh_token: str,
        user_manager: BaseUserManager[models.UP, models.ID],
    ) -> Response:
        strategy = self.get_strategy()

        new_access_token = await strategy.refresh_access_token(
            refresh_token, user_manager
        )

        if not new_access_token:
            raise HTTPException(
                status_code=401, detail="Invalid refresh token"
            )

        return JSONResponse(
            {"access_token": new_access_token, "token_type": "bearer"}
        )
