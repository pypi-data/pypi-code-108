import httpx
import pytest

from impressive_strawberry.database import tables

pytestmark = pytest.mark.asyncio


class TestWebhookList:
    async def test_success(self, authenticated_client: httpx.AsyncClient, webhook: tables.Webhook):
        response = await authenticated_client.get("/api/webhook/v1/", params={"group": webhook.group.crystal})
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1

        obj = data[0]
        assert obj.items() >= {
            "kind": "STRAWBERRY",
            "url": "https://example.org/testapp",
            "group_id": str(webhook.group.id),
        }.items()
        assert "id" in obj


class TestWebhookRetrieve:
    async def test_success(self, authenticated_client: httpx.AsyncClient, webhook: tables.Webhook):
        response = await authenticated_client.get(f"/api/webhook/v1/{webhook.id}", params={"group": webhook.group.crystal})
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= {
            "kind": "STRAWBERRY",
            "url": "https://example.org/testapp",
            "group_id": str(webhook.group.id),
        }.items()
        assert "id" in data
        assert "group" in data


class TestWebhookCreate:
    async def test_success(self, authenticated_client: httpx.AsyncClient, group: tables.Group):
        body = {
            "kind": "STRAWBERRY",
            "url": "https://example.org/testapp",
        }

        response = await authenticated_client.post("/api/webhook/v1/", params={"group": "test"}, json=body)
        assert response.status_code == 201

        data = response.json()
        assert data.items() >= body.items()


class TestWebhookUpdate:
    async def test_success(self, authenticated_client: httpx.AsyncClient, webhook: tables.Webhook):
        body = {
            "kind": "DISCORD",
            "url": "https://example.org/testapp",
        }

        response = await authenticated_client.put(f"/api/webhook/v1/{webhook.id}", params={"group": "test"}, json=body)
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= body.items()

        response = await authenticated_client.get(f"/api/webhook/v1/{webhook.id}", params={"group": "test"})
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= body.items()


class TestWebhookDelete:
    async def test_success(self, authenticated_client: httpx.AsyncClient, webhook: tables.Webhook):
        response = await authenticated_client.delete(f"/api/webhook/v1/{webhook.id}", params={"group": webhook.group.crystal})
        assert response.status_code == 204

        response = await authenticated_client.get(f"/api/webhook/v1/{webhook.id}", params={"group": webhook.group.crystal})
        assert response.status_code == 404
