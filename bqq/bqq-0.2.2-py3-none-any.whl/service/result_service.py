from typing import Optional

from bqq import const, Config
from bqq.bq_client import BqClient
from bqq.data.infos import Infos
from bqq.data.results import Results
from bqq.data.schemas import Schemas
from bqq.types import JobInfo
from google.api_core.exceptions import BadRequest, NotFound
from google.cloud.bigquery.job.query import QueryJob
from rich import box
from rich.console import Console
from rich.text import Text
from rich.table import Table


class ResultService:
    type_to_justify = {"STRING": "left", "INTEGER": "right"}

    def __init__(
        self, console: Console, config: Config, bq_client: BqClient, infos: Infos, results: Results, schemas: Schemas
    ):
        self.console = console
        self.config = config
        self.bq_client = bq_client
        self.infos = infos
        self.results = results
        self.schemas = schemas

    def write_result(self, query_job: QueryJob):
        try:
            rows = query_job.result(max_results=self.config.max_results)
            self.schemas.write(query_job.project, query_job.job_id, rows.schema)
            self.results.write(query_job.project, query_job.job_id, rows)
        except (BadRequest, NotFound) as e:
            self.infos.update_has_result(query_job.job_id, False)

    def download_result(self, job_id: str):
        job = self.bq_client.client.get_job(job_id)
        if isinstance(job, QueryJob):
            self.write_result(job)
        else:
            self.console.print(Text("Query job doesn't exist", style=const.error_style))

    def get_table(self, job_info: JobInfo) -> Optional[Table]:
        table = None
        schema = self.schemas.read(job_info)
        result = self.results.read(job_info)
        if schema and result:
            table = Table(box=box.ROUNDED, border_style=const.border_style, row_styles=["none", const.alternate_style])
            table.add_column(justify="right")
            for field, col in zip(schema, result.header):
                justify = self.type_to_justify.get(field.field_type, "left")
                table.add_column(col, justify=justify)
            for i, row in enumerate(result.rows):
                table.add_row(Text(f"{i + 1}", style=const.border_style), *row)
            measurement = table.__rich_measure__(self.console, self.console.options)
            table.width = measurement.maximum  # set maximum width (required for pager)
        return table
