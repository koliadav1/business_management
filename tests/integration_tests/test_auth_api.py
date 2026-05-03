import pytest


@pytest.mark.asyncio(loop_scope="session")
class TestAuthAPI:
    async def test_login_invalid_creds(self, client, test_user):
        response = await client.post(
            "/auth/login",
            data={"username": test_user.email, "password": "123"},
        )
        assert response.status_code == 400

    async def test_refresh_token_success(self, client, auth_headers):
        response = await client.post("/auth/refresh", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_refresh_token_no_header(self, client):
        response = await client.post("/auth/refresh")

        assert response.status_code == 400

    async def test_logout_success(self, client, auth_headers):
        response = await client.post("/auth/logout", headers=auth_headers)

        assert response.status_code == 200
