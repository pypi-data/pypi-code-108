import httpx
import pytest

from impressive_strawberry.database import tables

pytestmark = pytest.mark.asyncio


class TestUserRetrieve:
    async def test_success(self, authenticated_client: httpx.AsyncClient, user: tables.User):
        response = await authenticated_client.get(f"/api/user/v1/{user.crystal}")
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= {
            "crystal": "test",
        }.items()


class TestUserCreate:
    async def test_success(self, authenticated_client: httpx.AsyncClient, user: tables.User):
        body = {
            "crystal": "new",
        }

        response = await authenticated_client.post(f"/api/user/v1/", json=body)
        assert response.status_code == 201

        data = response.json()
        assert data.items() >= {
            "crystal": "new"
        }.items()


class TestUserUpdate:
    async def test_success(self, authenticated_client: httpx.AsyncClient, user: tables.User):
        body = {
            "crystal": "testone",
        }

        response = await authenticated_client.put(f"/api/user/v1/test", json=body)
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= {
            "crystal": "testone"
        }.items()

        response = await authenticated_client.get(f"/api/user/v1/testone")
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= {
            "crystal": "testone"
        }.items()


class TestUserDelete:
    async def test_success(self, authenticated_client: httpx.AsyncClient, user: tables.User):
        response = await authenticated_client.delete(f"/api/user/v1/test")
        assert response.status_code == 204

        response = await authenticated_client.get(f"/api/user/v1/test")
        assert response.status_code == 404
