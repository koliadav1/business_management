from httpx import AsyncClient
import pytest


@pytest.mark.asyncio(loop_scope="session")
class TestUsersAPI:
    async def test_update_user_name_success(
        self, client: AsyncClient, test_user, auth_headers
    ):
        update_data = {
            "name": "New name",
            "surname": "New surname",
            "phone_number": "321321",
        }

        response = await client.patch(
            "users/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["surname"] == update_data["surname"]
        assert data["phone_number"] == update_data["phone_number"]
        assert data["email"] == test_user.email

    async def test_update_email_with_password(
        self, client: AsyncClient, test_user, auth_headers
    ):
        new_email = "new@example.com"
        update_data = {
            "email": new_email,
            "current_password": test_user.plain_password,
        }

        response = await client.patch(
            "users/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == new_email

    async def test_update_email_without_password(
        self, client: AsyncClient, auth_headers
    ):
        new_email = "new@example.com"
        update_data = {
            "email": new_email,
        }

        response = await client.patch(
            "users/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 400
        data = response.json()
        assert "Current password needed" in data["detail"]

    async def test_update_email_with_invalid_password(
        self, client: AsyncClient, auth_headers
    ):
        new_email = "new@example.com"
        update_data = {
            "email": new_email,
            "current_password": "asda123",
        }

        response = await client.patch(
            "users/me", json=update_data, headers=auth_headers
        )

        assert response.status_code == 401
        data = response.json()
        assert "Invalid current password" in data["detail"]

    async def test_update_unauthorized(self, client: AsyncClient):
        response = await client.patch("users/me", json={"name": "asd"})

        assert response.status_code == 401

    async def test_delete_success(
        self, client: AsyncClient, test_user, auth_headers
    ):
        old_pass_hash = test_user.hashed_password
        delete_data = {"password": test_user.plain_password}
        response = await client.delete(
            "/users/me", params=delete_data, headers=auth_headers
        )
        assert response.status_code == 204
        assert test_user.is_active == False
        assert test_user.hashed_password != old_pass_hash
        assert test_user.name == None
        assert test_user.surname == None
        assert test_user.phone_number == None

    async def test_delete_invalid_password(
        self, client: AsyncClient, test_user, auth_headers
    ):
        delete_data = {"password": "asdasd"}
        response = await client.delete(
            "/users/me", params=delete_data, headers=auth_headers
        )

        assert response.status_code == 401
        assert test_user.is_active == True
