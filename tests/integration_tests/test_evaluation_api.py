import pytest


@pytest.mark.asyncio(loop_scope="session")
class TestEvaluationAPI:
    async def test_rate_task_success(
        self, client, admin_auth_headers, test_completed_task
    ):
        rate_data = {"rating": 3, "comment": "asdasd"}

        response = await client.post(
            f"/evaluations/rate/{test_completed_task.id}",
            json=rate_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == rate_data["rating"]
        assert data["comment"] == rate_data["comment"]
        assert data["task_id"] == test_completed_task.id

    async def test_get_evaluations_success(
        self,
        client,
        admin_auth_headers,
        test_evaluation,
    ):
        response = await client.get(
            "/evaluations/",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    async def test_get_evaluations_with_tasks_success(
        self,
        client,
        admin_auth_headers,
        test_completed_task,
        test_evaluation,
        test_team_with_members,
    ):
        response = await client.get(
            f"/evaluations/with-tasks?user_id={test_team_with_members["employee"].id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        assert "task" in data["items"][0]
        assert "evaluation" in data["items"][0]

    async def test_get_stats_success(
        self,
        client,
        admin_auth_headers,
        test_team_with_members,
    ):
        response = await client.get(
            f"/evaluations/stats?user_id={test_team_with_members["employee"].id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "average" in data
        assert "total" in data
        assert "distribution" in data

    async def test_delete_evaluation_success(
        self,
        client,
        admin_auth_headers,
        test_completed_task,
        test_evaluation,
    ):
        response = await client.delete(
            f"/evaluations/{test_completed_task.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 204
