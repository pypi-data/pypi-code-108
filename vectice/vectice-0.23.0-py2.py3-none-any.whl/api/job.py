from typing import Optional
from urllib.parse import urlencode

from vectice.entity import Job

from .Page import Page
from .json_object import JsonObject
from .output.job_output import JobOutput
from .output.paged_response import PagedResponse
from .project import ProjectApi


class JobApi(ProjectApi):
    def __init__(self, project_token: str, _token: Optional[str] = None, allow_self_certificate=True):
        super().__init__(project_token=project_token, _token=_token, allow_self_certificate=allow_self_certificate)
        self._job_path = super().api_base_path + "/job"

    @property
    def api_base_path(self) -> str:
        return self._job_path

    def list_jobs(self, search: str = None, page_index=Page.index, page_size=Page.size) -> PagedResponse[JobOutput]:
        queries = {"index": page_index, "size": page_size}
        if search:
            queries["search"] = search
        jobs = self._get(self.api_base_path + "?" + urlencode(queries))
        return PagedResponse(item_cls=JobOutput, total=jobs["total"], page=jobs["page"], items=jobs["items"])

    def create_job(self, job: JsonObject) -> JobOutput:
        if job.get("name") is None:
            raise ValueError('"name" must be provided in job.')
        if job.get("type") is None:
            job["type"] = "OTHER"
        return JobOutput(**self._post(self.api_base_path, job))

    def update_job(self, job_id: int, job: JsonObject) -> Job:
        return Job(self._put(self.api_base_path + "/" + str(job_id), job))
