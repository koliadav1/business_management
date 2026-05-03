import pytest


@pytest.mark.asyncio(loop_scope="session")
class TestTeamAPI:
    async def test_create_team_success(
        self, client, test_user, auth_headers, db_session
    ):
        team_data = {"name": "Test", "description": "32133"}

        response = await client.post(
            "/teams/", json=team_data, headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == team_data["name"]
        assert data["description"] == team_data["description"]
        assert "id" in data

    async def test_get_all_teams_success(self, client, test_team):
        response = await client.get("/teams/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    async def test_get_my_team_success(
        self, client, admin_auth_headers, test_team
    ):
        response = await client.get(
            "/teams/my-team", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_team["team"].id
        assert data["name"] == test_team["team"].name

    async def test_get_team_members_success(
        self, client, admin_auth_headers, test_team_with_members
    ):
        response = await client.get(
            "/teams/members", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    async def test_add_member_success(
        self, client, admin_auth_headers, test_user
    ):
        add_data = {"user_id": test_user.id, "role": "employee"}
        response = await client.post(
            "/teams/my-team/members", json=add_data, headers=admin_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == test_user.id
        assert data["role"] == "employee"

    async def test_remove_member_success(
        self, client, admin_auth_headers, test_team_with_members
    ):
        employee = test_team_with_members["employee"]

        response = await client.delete(
            f"/teams/my-team/members/{employee.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 204

    async def test_update_member_role_success(
        self, client, admin_auth_headers, test_team_with_members
    ):
        employee = test_team_with_members["employee"]
        upd_data = {"role": "manager"}

        response = await client.patch(
            f"/teams/my-team/members/{employee.id}/role",
            json=upd_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "manager"

    async def test_delete_team_success(
        self, client, admin_auth_headers, test_team
    ):
        response = await client.delete(
            "/teams/my-team", headers=admin_auth_headers
        )

        assert response.status_code == 204

    async def test_remove_self_success(
        self, client, employee_auth_headers, test_team_with_members
    ):
        response = await client.delete(
            "/teams/members/me", headers=employee_auth_headers
        )

        assert response.status_code == 204

    async def test_join_by_team_code_success(
        self, client, auth_headers, test_team
    ):
        join_data = {"invite_code": test_team["team"].invite_code}

        response = await client.post(
            "/teams/join", json=join_data, headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_team["team"].id
        assert data["name"] == test_team["team"].name

    async def test_get_team_code_success(
        self, client, admin_auth_headers, test_team
    ):
        response = await client.get(
            "/teams/my-team/invite-code", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["invite_code"] == test_team["team"].invite_code

    async def test_get_team_by_id_success(
        self, client, admin_auth_headers, test_team
    ):
        response = await client.get(
            f"/teams/{test_team["team"].id}", headers=admin_auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_team["team"].id
        assert data["name"] == test_team["team"].name
