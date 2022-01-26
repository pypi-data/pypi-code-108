from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ...models import CreateJobJsonBody, Job, StatusOK
from ..base import ApiBaseClass


class JobsApi(ApiBaseClass):
    """Endpoints related to various background jobs that can be run by the
    server or separately by job servers."""

    def get_jobs(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[Job]:
        """Get the jobs.

        Get a page of jobs. Use the query parameters to modify the behaviour of
        this endpoint.

        Permissions:
            Must have `manage_jobs` permission.
        Minimum Server Version:
            4.1
        """

        url = "/jobs".format()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Job.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def create_job(
        self,
        *,
        json_body: CreateJobJsonBody,
    ) -> Job:
        """Create a new job.

        Create a new job.

        Permissions:
            Must have `manage_jobs` permission.
        Minimum Server Version:
            4.1
        """

        url = "/jobs".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = Job.parse_obj(response.json())

            return response_201
        return response

    def get_job(
        self,
        job_id: str,
    ) -> Job:
        """Get a job.

        Gets a single job.

        Permissions:
            Must have `manage_jobs` permission.
        Minimum Server Version:
            4.1
        """

        url = "/jobs/{job_id}".format(
            job_id=job_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Job.parse_obj(response.json())

            return response_200
        return response

    def download_job(
        self,
        job_id: str,
    ) -> None:
        """Download the results of a job.

        Download the result of a single job.

        Permissions:
            Must have `manage_jobs` permission.
        Minimum Server Version:
            5.28
        """

        url = "/jobs/{job_id}/download".format(
            job_id=job_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    def cancel_job(
        self,
        job_id: str,
    ) -> StatusOK:
        """Cancel a job.

        Cancel a job.

        Permissions:
            Must have `manage_jobs` permission.
        Minimum Server Version:
            4.1
        """

        url = "/jobs/{job_id}/cancel".format(
            job_id=job_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def get_jobs_by_type(
        self,
        type: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[Job]:
        """Get the jobs of the given type.

        Get a page of jobs of the given type. Use the query parameters to modify
        the behaviour of this endpoint.

        Permissions:
            Must have `manage_jobs` permission.
        Minimum Server Version:
            4.1
        """

        url = "/jobs/type/{type}".format(
            type=type,
        )
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Job.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response
