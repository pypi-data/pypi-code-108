from google.cloud.bigquery.job.query import QueryJob
from rich.console import Group
from rich.text import Text

from bqq import const
from bqq.types import JobInfo
from bqq.util import bash_util, bq_util


def get_dry_info_header(job: QueryJob) -> Group:
    size = bq_util.size_fmt(job.total_bytes_processed)
    cost = bq_util.price_fmt(job.total_bytes_processed)
    return Group(
        Text("Billing project", style=const.info_style).append(f" = {job.project}", style="default"),
        Text("Estimated size", style=const.info_style).append(f" = {size}", style="default"),
        Text("Estimated cost", style=const.info_style).append(f" = {cost}", style="default"),
    )


def get_info_header(job_info: JobInfo) -> Group:
    cache_hit = "(cache hit)" if job_info.cache_hit else ""
    return Group(
        Text("Creation time", style=const.info_style).append(f" = {job_info.created_fmt}", style="default"),
        Text("Project", style=const.info_style).append(f" = {job_info.project}", style="default"),
        Text("Job Id", style=const.info_style).append(f" = {job_info.job_id}", style="default"),
        Text("Account", style=const.info_style).append(f" = {job_info.account}", style="default"),
        Text("Query cost", style=const.info_style).append(f" = {job_info.price_fmt} {cache_hit}", style="default"),
        Text("Slot time", style=const.info_style).append(f" = {job_info.slot_time}", style="default"),
        Text("Console link", style=const.info_style)
        .append(" = ", style="default")
        .append(job_info.google_link, style=const.link_style),
    )


def get_sql(job_info: JobInfo) -> Text:
    return bash_util.color_keywords(job_info.query)


def get_gcloud_info(json: dict) -> Group:
    project = json.get("config", {}).get("project")
    account = json.get("config", {}).get("account")
    return Group(
        Text("Project", style=const.info_style).append(f" = {project}", style="default"),
        Text("Account", style=const.info_style).append(f" = {account}", style="default"),
    )
