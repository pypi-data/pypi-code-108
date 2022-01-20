from typing import List, Optional

from bqq import const, output
from bqq.bq_client import BqClient
from bqq.config import Config
from bqq.data.infos import Infos
from bqq.service.result_service import ResultService
from bqq.types import JobInfo, SearchLine
from bqq.util import bash_util
from google.api_core.exceptions import BadRequest
from google.cloud.bigquery.job.query import QueryJob, QueryJobConfig
from rich.console import Console
from rich.prompt import Confirm
from rich.text import Text


class InfoService:
    def __init__(
        self,
        console: Console,
        config: Config,
        bq_client: BqClient,
        result_service: ResultService,
        infos: Infos,
    ) -> None:
        self.console = console
        self.config = config
        self.infos = infos
        self.bq_client = bq_client
        self.result_service = result_service

    def search(self) -> List[JobInfo]:
        rows = self.infos.search(self.config.project)
        choices = []
        for row in rows:
            search_line = SearchLine.from_job_info(row)
            choices.append(search_line.to_line(self.console))
        lines = bash_util.fzf(choices, multi=True, key=SearchLine.sort_key)
        infos = []
        for line in lines:
            search_line = SearchLine.from_line(line)
            if search_line:
                job_info = next((row for row in rows if row.job_id == search_line.job_id), None)
                infos.append(job_info)
        return infos

    def search_one(self) -> JobInfo:
        rows = self.infos.search(self.config.project)
        choices = []
        for row in rows:
            search_line = SearchLine.from_job_info(row)
            choices.append(search_line.to_line(self.console))
        lines = bash_util.fzf(choices, key=SearchLine.sort_key)
        search_line = next((SearchLine.from_line(line) for line in lines), None)
        job_info = None
        if search_line:
            job_info = next((row for row in rows if row.job_id == search_line.job_id), None)
        return job_info

    def sync_infos(self):
        jobs = self.bq_client.list_query_jobs()
        for job in jobs:
            job_info = JobInfo.from_query_job(job)
            self.infos.upsert(job_info)
        text = Text("Jobs synchronized", style=const.info_style).append(f" = {len(jobs)}", style="default")
        self.console.print(text)

    def dry_run(self, query: str) -> Optional[QueryJob]:
        job_config = QueryJobConfig()
        job_config.dry_run = True
        job = None
        try:
            job = self.bq_client.client.query(query, job_config=job_config)
        except BadRequest as e:
            self.console.print(e.message, style=const.error_style)
        return job

    def get_info(self, skip: bool, query: str) -> JobInfo:
        job_info = None
        confirmed = skip
        if not skip:
            job = self.dry_run(query)
            if job:
                headers = output.get_dry_info_header(job)
                self.console.print(headers)
                confirmed = Confirm.ask(
                    Text("", style=const.darker_style).append("Do you want to continue?", style=const.request_style),
                    default=False,
                    console=self.console,
                )
        if confirmed:
            query_job = self.bq_client.client.query(query)
            self.result_service.write_result(query_job)  # extract result before job info
            job_info = JobInfo.from_query_job(query_job)
            self.infos.insert(job_info)
        return job_info

    def delete_infos(self, jobs: List[JobInfo]):
        for job_info in jobs:
            self.bq_client.client.delete_job_metadata(
                job_id=job_info.job_id, project=job_info.project, location=job_info.location
            )
            self.infos.remove(job_info)
            self.console.print(
                Text("Job deleted", style=const.info_style).append(f": {job_info.job_id}", style=const.darker_style)
            )
