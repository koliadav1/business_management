import pytest


@pytest.mark.asyncio(loop_scope="session")
class TestCommentAPI:
    async def test_add_comment_success(
        self, client, admin_auth_headers, test_task
    ):
        comment_data = {"content": "test123"}

        response = await client.post(
            f"/comments/{test_task.id}",
            json=comment_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == comment_data["content"]
        assert data["task_id"] == test_task.id
        assert "author_id" in data

    async def test_get_comments_success(
        self, client, admin_auth_headers, test_task, test_comment
    ):
        response = await client.get(
            f"/comments/{test_task.id}",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["content"] == test_comment.content
        assert data[0]["task_id"] == test_task.id

    async def test_update_comment_success(
        self, client, admin_auth_headers, test_comment
    ):
        update_data = {"content": "upd test"}

        response = await client.patch(
            f"/comments/{test_comment.id}",
            json=update_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["content"] == update_data["content"]
        assert data["id"] == test_comment.id

    async def test_delete_comment_success(
        self, client, admin_auth_headers, test_comment
    ):
        response = await client.delete(
            f"/comments/{test_comment.id}", headers=admin_auth_headers
        )

        assert response.status_code == 204
