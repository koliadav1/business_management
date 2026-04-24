from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi_users.authentication import BearerTransport
from fastapi_users.openapi import OpenAPIResponseType
from pydantic import BaseModel


class BearerResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class BearerRefreshTransport(BearerTransport):
    refresh_token_header = "X-Refresh-Token"

    def __init__(self, tokenUrl):
        super().__init__(tokenUrl)

    async def get_login_response(
        self, token: str, refresh_token: str
    ) -> Response:
        bearer_response = BearerResponse(
            access_token=token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
        return JSONResponse(bearer_response.model_dump())

    async def get_access_token_from_request(
        self, request: Request
    ) -> str | None:
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None
        return auth[7:]

    async def get_refresh_token_from_request(
        self, request: Request
    ) -> str | None:
        return request.headers.get(self.refresh_token_header)

    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponse,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJI....",
                            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJ....",
                            "token_type": "bearer",
                        }
                    }
                },
            },
        }
