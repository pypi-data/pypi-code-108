import httpx
import pytest

from impressive_strawberry.database import tables

pytestmark = pytest.mark.asyncio


class TestAchievementList:
    async def test_success(self, authenticated_client: httpx.AsyncClient, achievement: tables.Achievement):
        response = await authenticated_client.get("/api/achievement/v1/", params={"group": "test"})
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1

        obj = data[0]
        assert obj.items() >= {
            "name": "Test Achievement",
            "description": "Achievement unlocked when testing achievement unlocks.",
            "alloy": "BRONZE",
            "secret": False,
            "icon": None,
            "repeatable": False,
            "crystal": "test",
        }.items()


class TestAchievementRetrieve:
    async def test_success(self, authenticated_client: httpx.AsyncClient, achievement: tables.Achievement):
        response = await authenticated_client.get("/api/achievement/v1/test", params={"group": "test"})
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= {
            "name": "Test Achievement",
            "description": "Achievement unlocked when testing achievement unlocks.",
            "alloy": "BRONZE",
            "secret": False,
            "icon": None,
            "repeatable": False,
            "crystal": "test",
        }.items()


class TestAchievementCreate:
    async def test_success(self, authenticated_client: httpx.AsyncClient, group: tables.Group):
        body = {
            "name": "My Little Achievement",
            "description": "A fun little achievement to unlock with friends!",
            "alloy": "SILVER",
            "secret": False,
            "icon": None,
            "repeatable": False,
            "crystal": "mla",
        }

        response = await authenticated_client.post("/api/achievement/v1/", params={"group": "test"}, json=body)
        assert response.status_code == 201

        data = response.json()
        assert data.items() >= body.items()


class TestAchievementUpdate:
    async def test_success(self, authenticated_client: httpx.AsyncClient, achievement: tables.Achievement):
        body = {
            "name": "Test Achievement",
            "description": "Achievement unlocked when testing achievement unlocks.",
            "alloy": "GOLD",
            "secret": False,
            "icon": None,
            "repeatable": False,
            "crystal": "test",
        }

        response = await authenticated_client.put("/api/achievement/v1/test", params={"group": "test"}, json=body)
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= body.items()

        response = await authenticated_client.get("/api/achievement/v1/test", params={"group": "test"})
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= body.items()


class TestAchievementDelete:
    async def test_success(self, authenticated_client: httpx.AsyncClient, achievement: tables.Achievement):
        response = await authenticated_client.delete("/api/achievement/v1/test", params={"group": "test"})
        assert response.status_code == 204

        response = await authenticated_client.get("/api/achievement/v1/test", params={"group": "test"})
        assert response.status_code == 404
