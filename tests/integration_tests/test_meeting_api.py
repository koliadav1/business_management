from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.asyncio(loop_scope="session")
class TestMeetingAPI:
    async def test_add_meeting_success(
        self,
        client,
        admin_auth_headers,
        test_team_with_members,
    ):
        meeting_data = {
            "description": "test meeting",
            "start_time": (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).isoformat(),
            "duration_m": 60,
            "member_ids": [test_team_with_members["employee"].id],
        }

        response = await client.post(
            "/meetings/",
            json=meeting_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["description"] == meeting_data["description"]
        assert data["duration_m"] == meeting_data["duration_m"]

    async def test_get_user_meetings_success(
        self,
        client,
        admin_auth_headers,
        test_meeting,
    ):
        response = await client.get("/meetings/", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_team_meetings_success(
        self,
        client,
        admin_auth_headers,
        test_meeting,
    ):
        response = await client.get(
            "/meetings/team", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_upcoming_meetings_success(
        self,
        client,
        admin_auth_headers,
        test_meeting,
    ):
        response = await client.get(
            "/meetings/upcoming",
            params={"minutes_ahead": 1440},
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_meeting_success(
        self,
        client,
        admin_auth_headers,
        test_meeting,
    ):
        response = await client.get(
            f"/meetings/{test_meeting.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_meeting.id
        assert data["description"] == test_meeting.description
        assert "members" in data

    async def test_update_meeting_success(
        self,
        client,
        admin_auth_headers,
        test_meeting,
    ):
        update_data = {"description": "test2"}

        response = await client.patch(
            f"/meetings/{test_meeting.id}",
            json=update_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == test_meeting.description

    async def test_cancel_meeting_success(
        self,
        client,
        admin_auth_headers,
        test_meeting,
    ):
        response = await client.patch(
            f"/meetings/{test_meeting.id}/cancel",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    async def test_add_members_to_meeting_success(
        self,
        client,
        admin_auth_headers,
        test_meeting,
        test_team_with_members,
    ):
        add_data = {"member_ids": [test_team_with_members["manager"].id]}

        response = await client.post(
            f"/meetings/{test_meeting.id}/members",
            json=add_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        member_ids = [member["id"] for member in data["members"]]
        assert test_team_with_members["manager"].id in member_ids

    async def test_remove_member_from_meeting_success(
        self,
        client,
        admin_auth_headers,
        test_meeting,
        test_team_with_members,
    ):
        remove_data = {"member_id": test_team_with_members["employee"].id}

        response = await client.request(
            "DELETE",
            f"/meetings/{test_meeting.id}/members",
            json=remove_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 204
