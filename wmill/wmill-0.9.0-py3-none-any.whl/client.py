from typing import Any, Union, Dict

import attr
import os
from time import sleep

from windmill_api.client import AuthenticatedClient
from windmill_api.api.settings import backend_version
from windmill_api.api.job import run_script_by_hash, get_job, get_completed_job
from windmill_api.api.resource import get_resource
from windmill_api.models.get_job_response_200_type import GetJobResponse200Type

from windmill_api.models.run_script_by_hash_json_body import RunScriptByHashJsonBody

from enum import Enum

from windmill_api.types import Unset


VAR_RESOURCE_PREFIX = "$VAR:"


class JobStatus(Enum):
    WAITING = 1
    RUNNING = 2
    COMPLETED = 3


@attr.s(auto_attribs=True)
class Client:
    """
    Client to interact with the Windmill API
    """

    base_url: str = "http://localhost:8000/api"
    token: str = os.environ.get("WM_TOKEN") or ""

    def __attrs_post_init__(self):
        self.client = AuthenticatedClient(base_url=self.base_url, token=self.token, timeout=30, verify_ssl=False)

    def get_version(self) -> str:
        """
        Returns the current version of the backend
        """
        return backend_version.sync_detailed(client=self.client).content.decode("us-ascii")

    def run_script_async(
        self,
        hash: str,
        args: Dict[str, Any] = {},
        scheduled_in_secs: Union[None, float] = None,
    ) -> str:
        """
        Launch the run of a script and return immediately its job id
        """
        return run_script_by_hash.sync_detailed(
            client=self.client,
            hash_=hash,
            json_body=RunScriptByHashJsonBody.from_dict(args),
            scheduled_in_secs=scheduled_in_secs,
            parent_job=os.environ.get("DT_JOB_ID"),
        ).content.decode("us-ascii")

    def run_script_sync(self, hash: str, args: Dict[str, Any] = {}, verbose: bool = False) -> Dict[str, Any]:
        """
        Run a script, wait for it to complete and return the result of the launched script
        """
        job_id = self.run_script_async(hash, args, None)
        nb_iter = 0
        while self.get_job_status(job_id) != JobStatus.COMPLETED:
            if verbose:
                print(f"Waiting for {job_id} to complete...")
            if nb_iter < 10:
                sleep(2.0)
            else:
                sleep(5.0)
            nb_iter += 1
        return self.get_result(job_id)

    def get_job_status(self, job_id: str) -> JobStatus:
        """
        Returns the status of a queued or completed job
        """
        res = get_job.sync_detailed(client=self.client, id=job_id).parsed
        if not res:
            raise Exception(f"Job {job_id} not found")
        elif not res.type:
            raise Exception(f"Unexpected type not found for job {job_id}")
        elif res.type == GetJobResponse200Type.COMPLETEDJOB:
            return JobStatus.COMPLETED
        else:
            if not "running" in res.additional_properties:
                raise Exception(f"Unexpected running not found for completed job {job_id}")
            elif bool(res.additional_properties["running"]):
                return JobStatus.RUNNING
            else:
                return JobStatus.WAITING

    def get_result(self, job_id: str) -> Dict[str, Any]:
        """
        Returns the result of a completed job
        """
        res = get_completed_job.sync_detailed(client=self.client, id=job_id).parsed
        if not res:
            raise Exception(f"Job {job_id} not found")
        if not res.result:
            raise Exception(f"Unexpected result not found for completed job {job_id}")
        else:
            return res.result.to_dict()  # type: ignore

    def get_resource(self, path: str) -> Dict[str, Any]:
        """
        Returns a resource at a given path as a python dict.
        """
        parsed = get_resource.sync_detailed(path=path, client=self.client).parsed
        if parsed is None:
            raise Exception(f"Resource {path} not found")

        if isinstance(parsed.value, Unset):
            return {}

        raw_dict = parsed.value.to_dict()
        res = Client._transform_leaves(raw_dict)

        return res

    @staticmethod
    def _transform_leaves(d: Dict[str, Any]) -> Dict[str, Any]:
        return {k: Client._transform_leaf(v) for k, v in d.items()}

    @staticmethod
    def _transform_leaf(v: Any) -> Any:
        if isinstance(v, dict):
            return Client._transform_leaves(v)  # type: ignore
        elif isinstance(v, str):
            if v.startswith(VAR_RESOURCE_PREFIX):
                var_name = v[len(VAR_RESOURCE_PREFIX) :]
                return os.environ.get(var_name, f"VARIABLE ${var_name} NOT ACCESSIBLE")
            else:
                return v
        else:
            return v
