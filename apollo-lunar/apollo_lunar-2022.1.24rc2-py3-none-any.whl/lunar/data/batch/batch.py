from typing import Any, Dict, List

import asyncio

from lunar.config import Config
from lunar.lunar_client import LunarClient
from lunar.data.batch.models import BatchJobsIn

loop = asyncio.get_event_loop()


class BatchClient(LunarClient):
    """
    Client for Lunar Data API (`/v1/batch`).

    ## Example

    ```python
    import lunar

    client = lunar.client("batch")
    ```
    """

    def __init__(self, config: Config):
        super().__init__(config)

    async def get_batch_list_async(self, job_status_list: List[str]) -> List[Dict[str, Any]]:
        """
        Get a list of batch jobs (async).

        ## Args

        - job_status_list: (list) List of job_status of Batch ('SUBMITTED' | 'PENDING' | 'RUNNABLE' | 'STARTING' | 'RUNNING' | 'SUCCEEDED' | 'FAILED')

        ## Returns
        list

        ## Example

        ```python
        data = await client.get_batch_list_async(job_status_list=["STARTING", "RUNNING"])

        ```
        """
        jobs_in = BatchJobsIn(job_status=job_status_list)
        params = {"job_status": [job.value for job in jobs_in.job_status]}

        body = await self._request(method="GET", url=self.config.API_PATH, params=params)

        return body["data"]

    def get_batch_list(self, job_status_list: List[str]) -> List[Dict[str, Any]]:
        """
        Get a list of batch jobs.

        ## Args

        - job_status_list: (list) List of job_status of Batch ('SUBMITTED' | 'PENDING' | 'RUNNABLE' | 'STARTING' | 'RUNNING' | 'SUCCEEDED' | 'FAILED')

        ## Returns
        list

        ## Example

        ```python
        data = client.get_batch_list(job_status_list=["STARTING", "RUNNING"])

        ```
        """

        return loop.run_until_complete(self.get_batch_list_async(job_status_list=job_status_list))
