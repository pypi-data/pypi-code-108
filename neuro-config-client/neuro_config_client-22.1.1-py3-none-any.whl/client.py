from __future__ import annotations

import logging
from collections.abc import Sequence
from types import TracebackType
from typing import Any

import aiohttp
from aiohttp import ClientResponseError, payload
from yarl import URL

from .converters import PrimitiveToClusterConverter
from .models import Cluster

logger = logging.getLogger(__name__)


class ConfigClient:
    def __init__(
        self,
        url: URL,
        token: str,
        timeout: aiohttp.ClientTimeout = aiohttp.client.DEFAULT_TIMEOUT,
        trace_configs: Sequence[aiohttp.TraceConfig] = (),
    ):
        self._clusters_url = url / "api/v1/clusters"
        self._token = token
        self._timeout = timeout
        self._trace_configs = trace_configs
        self._client: aiohttp.ClientSession | None = None
        self._primitive_to_cluster_converter = PrimitiveToClusterConverter()

    async def __aenter__(self) -> "ConfigClient":
        self._client = await self._create_http_client()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        assert self._client
        await self._client.close()

    async def _create_http_client(self) -> aiohttp.ClientSession:
        client = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self._token}"},
            timeout=self._timeout,
            trace_configs=list(self._trace_configs),
        )
        return await client.__aenter__()

    async def get_clusters(self) -> Sequence[Cluster]:
        assert self._client
        async with self._client.get(
            self._clusters_url, params={"include": "all"}
        ) as response:
            response.raise_for_status()
            payload = await response.json()
            return [
                self._primitive_to_cluster_converter.convert_cluster(p) for p in payload
            ]

    async def get_cluster(self, name: str) -> Cluster:
        assert self._client
        async with self._client.get(
            self._clusters_url / name, params={"include": "all"}
        ) as response:
            response.raise_for_status()
            payload = await response.json()
            return self._primitive_to_cluster_converter.convert_cluster(payload)

    async def create_blank_cluster(
        self, name: str, token: str, ignore_existing: bool = False
    ) -> None:
        assert self._client
        payload = {"name": name, "token": token}
        try:
            async with self._client.post(self._clusters_url, json=payload) as resp:
                resp.raise_for_status()
        except ClientResponseError as e:
            is_existing = e.status == 400 and "already exists" in e.message
            if not ignore_existing or is_existing:
                raise

    async def delete_cluster(self, name: str) -> None:
        assert self._client
        async with self._client.delete(self._clusters_url / name) as resp:
            resp.raise_for_status()

    async def add_storage(
        self,
        cluster_name: str,
        storage_name: str,
        size_mb: int | None = None,
        *,
        start_deployment: bool = True,
    ) -> None:
        assert self._client
        url = self._clusters_url / cluster_name / "cloud_provider/storages"
        payload: dict[str, Any] = {"name": storage_name}
        if size_mb is not None:
            payload["size_mb"] = size_mb
        async with self._client.post(
            url.with_query(start_deployment=str(start_deployment).lower()),
            json=payload,
        ) as response:
            response.raise_for_status()

    async def remove_storage(
        self,
        cluster_name: str,
        storage_name: str,
        *,
        start_deployment: bool = True,
    ) -> None:
        assert self._client
        url = (
            self._clusters_url / cluster_name / "cloud_provider/storages" / storage_name
        )
        async with self._client.delete(
            url.with_query(start_deployment=str(start_deployment).lower()),
            json=payload,
        ) as response:
            response.raise_for_status()
