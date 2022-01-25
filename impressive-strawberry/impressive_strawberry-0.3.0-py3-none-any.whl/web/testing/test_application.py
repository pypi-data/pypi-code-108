import httpx
import pytest

from impressive_strawberry.database import tables

pytestmark = pytest.mark.asyncio


class TestApplicationCreate:
    async def test_success_without_secret(self, client: httpx.AsyncClient, impressive_secret_unset: None):
        body = {
            "name": "Closure Industries Bot",
            "description": "A bot for achievements in a warpgate-based game.",
        }

        response = await client.post("/api/application/v1/", json=body)
        assert response.status_code == 201

        data = response.json()
        assert data.items() >= body.items()
        assert "id" in data
        assert "token" in data
        assert data["groups"] == []
        assert data["users"] == []

    async def test_success_with_secret(self, client: httpx.AsyncClient, impressive_secret: str):
        body = {
            "name": "Closure Industries Bot",
            "description": "A bot for achievements in a warpgate-based game.",
        }

        response = await client.post("/api/application/v1/", json=body, headers={
            "Authorization": f"Secret {impressive_secret}"
        })
        assert response.status_code == 201

        data = response.json()
        assert data.items() >= body.items()
        assert "id" in data
        assert "token" in data
        assert data["groups"] == []
        assert data["users"] == []

    async def test_missing_secret(self, client: httpx.AsyncClient, impressive_secret: str):
        response = await client.post("/api/application/v1/")
        assert response.status_code == 401

        data = response.json()
        assert data["error_code"] == "MISSING_AUTH_HEADER"

    async def test_invalid_secret(self, client: httpx.AsyncClient, impressive_secret: str):
        response = await client.post("/api/application/v1/", headers={
            "Authorization": "asjduisjfisdjgfiasj",
        })
        assert response.status_code == 401

        data = response.json()
        assert data["error_code"] == "INVALID_AUTH_HEADER"

    async def test_wrong_secret(self, client: httpx.AsyncClient, impressive_secret: str):
        response = await client.post("/api/application/v1/", headers={
            "Authorization": "Secret xyzzy",
        })
        assert response.status_code == 401

        data = response.json()
        assert data["error_code"] == "WRONG_AUTH_HEADER"

    async def test_missing_body(self, client: httpx.AsyncClient, impressive_secret_unset: None):
        response = await client.post("/api/application/v1/")
        assert response.status_code == 422

    async def test_invalid_body(self, client: httpx.AsyncClient, impressive_secret_unset: None):
        body = {
            "name": "Failure App",
        }

        response = await client.post("/api/application/v1/", json=body)
        assert response.status_code == 422


class TestApplicationThisRetrieve:
    async def test_success(self, authenticated_client: httpx.AsyncClient, application: tables.Application):
        response = await authenticated_client.get("/api/application/v1/this")
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= {
            "name": application.name,
            "description": application.description,
            "token": application.token,
        }.items()

    async def test_missing_auth(self, client: httpx.AsyncClient):
        response = await client.get("/api/application/v1/this")
        assert response.status_code == 401

    async def test_invalid_auth(self, client: httpx.AsyncClient):
        response = await client.get("/api/application/v1/this", headers={
            "Authorization": "Bearer INVALID",
        })
        assert response.status_code == 401


class TestApplicationThisUpdate:
    async def test_success(self, authenticated_client: httpx.AsyncClient, application: tables.Application):
        body = {
            "name": application.name,
            "description": application.description,
        }

        response = await authenticated_client.put("/api/application/v1/this", json=body)
        assert response.status_code == 200

        data = response.json()
        assert data.items() >= body.items()


class TestApplicationThisDelete:
    async def test_success(self, authenticated_client: httpx.AsyncClient, application: tables.Application):
        response = await authenticated_client.delete("/api/application/v1/this")
        assert response.status_code == 204

        response = await authenticated_client.get("/api/application/v1/this")
        assert response.status_code == 401


class TestApplicationThisRevoke:
    async def test_success(self, authenticated_client: httpx.AsyncClient, application: tables.Application):
        previous_token = application.token

        response = await authenticated_client.patch("/api/application/v1/this/revoke")
        assert response.status_code == 200

        data = response.json()
        assert "token" in data
        assert previous_token != data["token"]

        response = await authenticated_client.get("/api/application/v1/this")
        assert response.status_code == 401
