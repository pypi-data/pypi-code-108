from typing import List, Optional
from urllib.parse import urlencode

from vectice.entity import Run

from .Page import Page
from .job import JobApi
from .json_object import JsonObject
from .output.job_run_output import JobRunOutput


class RunApi(JobApi):
    def __init__(self, project_token: str, job_id: int, _token: Optional[str] = None, allow_self_certificate=True):
        super().__init__(project_token=project_token, _token=_token, allow_self_certificate=allow_self_certificate)
        self._job_id = job_id
        self._run_path = super().api_base_path + "/" + str(job_id) + "/run"

    @property
    def job_id(self) -> int:
        return self._job_id

    @property
    def api_base_path(self) -> str:
        return self._run_path

    def list_runs(self, page_index=Page.index, page_size=Page.size) -> List[JobRunOutput]:
        queries = {"index": page_index, "size": page_size}
        runs = self._get(self.api_base_path + "?" + urlencode(queries))["items"]
        return [JobRunOutput(**run) for run in runs]

    def create_run(self, run: JsonObject) -> Run:
        if run.get("status") is None:
            raise ValueError('"status" must be provided in run.')
        if run.get("startDate") is None:
            raise ValueError('"startDate" must be provided in run.')
        return Run(self._post(self.api_base_path, run))

    def update_run(self, run_id: int, run: JsonObject) -> Run:
        return Run(self._put(self.api_base_path + "/" + str(run_id), run))
