from datetime import datetime, timedelta, timezone

import pytest


@pytest.mark.asyncio(loop_scope="session")
class TestTaskAPI:
    async def test_create_task_success(
        self, client, admin_auth_headers, test_team_with_members
    ):
        task_data = {
            "description": "test",
            "deadline": (
                datetime.now(timezone.utc) + timedelta(days=7)
            ).isoformat(),
            "executor_id": test_team_with_members["employee"].id,
        }

        response = await client.post(
            "/tasks/", json=task_data, headers=admin_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["description"] == task_data["description"]
        assert data["executor_id"] == task_data["executor_id"]
        assert data["status"] == "new"

    async def test_get_user_tasks_success(
        self, client, admin_auth_headers, test_task
    ):
        response = await client.get(
            f"/tasks/?user_id={test_task.executor_id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    async def test_get_done_tasks_with_evaluations_success(
        self, client, admin_auth_headers, test_done_task_with_evaluation
    ):
        response = await client.get("/tasks/done", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        assert "evaluation" in data["items"][0]
        assert "task" in data["items"][0]

    async def test_get_team_tasks_success(
        self, client, admin_auth_headers, test_task
    ):
        response = await client.get("/tasks/team", headers=admin_auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1

    async def test_get_user_overdue_tasks_success(
        self, client, employee_auth_headers
    ):
        response = await client.get(
            "/tasks/overdue", headers=employee_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_get_team_overdue_tasks_success(
        self, client, admin_auth_headers
    ):
        response = await client.get(
            "/tasks/team/overdue", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_get_task_success(
        self, client, admin_auth_headers, test_task
    ):
        response = await client.get(
            f"/tasks/{test_task.id}", headers=admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_task.id
        assert data["description"] == test_task.description

    async def test_update_task_success(
        self, client, admin_auth_headers, test_task
    ):
        update_data = {"description": "asdads"}

        response = await client.patch(
            f"/tasks/{test_task.id}",
            json=update_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]

    async def test_assign_executor_success(
        self, client, admin_auth_headers, test_task, test_team_with_members
    ):
        assign_data = {
            "executor_id": test_team_with_members["another_employee"].id
        }

        response = await client.patch(
            f"/tasks/{test_task.id}/executor",
            json=assign_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["executor_id"] == assign_data["executor_id"]

    async def test_change_status_success(
        self, client, admin_auth_headers, test_task
    ):
        status_data = {"status": "in_progress"}

        response = await client.patch(
            f"/tasks/{test_task.id}/status",
            json=status_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == status_data["status"]

    async def test_delete_task_success(
        self, client, admin_auth_headers, test_task
    ):
        response = await client.delete(
            f"/tasks/{test_task.id}", headers=admin_auth_headers
        )

        assert response.status_code == 204
