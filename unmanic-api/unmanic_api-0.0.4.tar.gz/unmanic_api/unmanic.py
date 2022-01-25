"""Asynchronous Python client for Unmanic."""
from typing import Dict, List, Optional
from aiohttp.client import ClientSession
import json

from .client import Client
from .exceptions import UnmanicError

from .models import (
    Worker,
    Settings,
    PendingTask,
    TaskQueue,
)


class Unmanic(Client):
    """
    Main class for Python API.

    Args:

    host: The hostname or IP address of the Unmanic server.

    port: The port number of the Unmanic server.

    base_path: The base path of the API on the Unmanic server.

    request_timeout: The request timeout in seconds.

    session: The aiohttp.ClientSession to use.

    tls: Whether to use TLS.

    verify_ssl: Whether to verify the SSL certificate.

    user_agent: The user agent to use.
    """

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 8888,
        base_path: str = "/unmanic/api/",
        request_timeout: int = 8,
        session: ClientSession = None,
        tls: bool = False,
        verify_ssl: bool = True,
        user_agent: str = None,
    ) -> None:
        """Initilize connection with Unmanic"""
        super().__init__(
            host=host,
            base_path=base_path,
            port=port,
            request_timeout=request_timeout,
            session=session,
            tls=tls,
            verify_ssl=verify_ssl,
            user_agent=user_agent,
        )

    async def get_installation_name(self) -> str:
        """
        Get Unmanic installation name

        Returns:
            str: Unmanic installation name
        """
        results = await self.get_settings()
        return results.installation_name

    async def get_version(self) -> str:
        """
        Get Unmanic version

        Returns:
            str: Unmanic server version
        """
        results = await self._request("v2/version/read")
        return results['version']

    async def pause_worker(self, worker_id: str) -> bool:
        """
        Pause a worker

        Args:

        worker_id: The worker id.

        Returns:
            bool: True if successful.
        """
        results = await self._request(f"v2/workers/worker/pause", method='POST', data=json.dumps({"worker_id": worker_id}))
        return results['success']

    async def pause_all_workers(self) -> bool:
        """
        Pause all workers

        Returns:
            bool: True if successful.
        """
        results = await self._request("v2/workers/worker/pause/all", method='POST')
        return results['success']

    async def resume_worker(self, worker_id: str) -> bool:
        """
        Resume a worker

        Args:

        worker_id: The worker id.

        Returns:
            bool: True if successful.
        """
        results = await self._request(f"v2/workers/worker/resume", method='POST', data=json.dumps({"worker_id": worker_id}))
        return results['success']

    async def resume_all_workers(self) -> bool:
        """
        Resume all workers

        Returns:
            bool: True if successful.
        """
        results = await self._request("v2/workers/worker/resume/all", method='POST')
        return results['success']

    async def terminate_worker(self, worker_id) -> bool:
        """
        Terminate a worker

        Args:

        worker_id: The worker id.

        Returns:
            bool: True if successful.
        """
        results = await self._request("v2/workers/worker/terminate", method='POST', data=json.dumps({"worker_id": worker_id}))
        return results['success']

    async def get_workers_status(self) -> List[Worker]:
        """
        Get workers status

        Returns:
            Dict: Workers status
        """
        results = await self._request("v2/workers/status")
        return [Worker.from_dict(result) for result in results['workers_status']]

    async def get_settings(self) -> Settings:
        """
        Get Unmanic settings

        Returns:
            Dict: Unmanic server settings
        """
        results = await self._request("v2/settings/read")
        return Settings.from_dict(results['settings'])

    async def set_settings(self, settings: Dict) -> bool:
        """
        Set Unmanic settings

        Args:

        settings: The settings to set.

        Returns:
            bool: True if successful.
        """
        results = await self._request("v2/settings/write", method='POST', data=json.dumps({'settings': settings}))
        return results['success']

    async def get_workers_count(self) -> int:
        """
        Get workers count

        Returns:
            int: Number of workers
        """
        results = await self.get_settings()
        return results.number_of_workers

    async def set_workers_count(self, number_of_workers: int) -> bool:
        """
        Set workers count

        Args:

        number_of_workers: The number of workers.

        Returns:
            bool: True if successful.
        """
        results = await self.set_settings({'number_of_workers': number_of_workers})
        return results

    async def trigger_library_scan(self) -> bool:
        """
        Trigger library scan

        Returns:
            bool: True if successful.
        """
        results = await self._request("v1/pending/rescan", method='GET')
        return results['success']

    async def get_pending_tasks(self, start=0, length=10, search_value="", order_by="priority", order_direction="desc") -> List[PendingTask]:
        """
        Get pending tasks

        Returns:
            Dict: TaskQueue
        """
        results = await self._request("v2/pending/tasks", method='POST', data=json.dumps({'start': start, 'length': length, 'search_value': search_value, 'order_by': order_by, 'order_direction': order_direction}))
        return TaskQueue.from_dict(results)

    async def __aenter__(self) -> "Unmanic":
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close_session()
