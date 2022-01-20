import json
import os
import subprocess
from pathlib import Path

import click
from rich.console import Console, Group, NewLine
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.text import Text

from bqq import const, output
from bqq.auth import Auth
from bqq.bq_client import BqClient
from bqq.config import Config
from bqq.data.infos import Infos
from bqq.data.results import Results
from bqq.data.schemas import Schemas
from bqq.service.info_service import InfoService
from bqq.service.project_service import ProjectService
from bqq.service.result_service import ResultService
from bqq.service.schema_service import SchemaService


@click.command()
@click.argument("sql", required=False)
@click.option("-f", "--file", help="File containing SQL", type=click.File("r"))
@click.option("-y", "--yes", help="Automatic yes to prompt", is_flag=True)
@click.option("-h", "--history", help="Search local history", is_flag=True)
@click.option("--delete", help="Delete job from history (local & cloud)", is_flag=True)
@click.option("--clear", help="Clear local history", is_flag=True)
@click.option("--schema", help="Show schema", is_flag=True)
@click.option("--sync", help="Synchronize job history from cloud", is_flag=True)
@click.option("--init", help="Initialize bqq environment", is_flag=True)
@click.option("--set-project", help="Set project for queries", is_flag=True)
@click.version_option()
def cli(
    sql: str,
    file: str,
    yes: bool,
    history: bool,
    delete: bool,
    clear: bool,
    schema: bool,
    sync: bool,
    init: bool,
    set_project: bool,
):
    """BiqQuery query."""
    ctx = click.get_current_context()
    config = Config(config_path=const.BQQ_CONFIG)
    console = Console(theme=const.theme, soft_wrap=True)
    auth = Auth(config, console)
    bq_client = BqClient(console, config)
    infos = Infos()
    results = Results(console)
    schemas = Schemas()
    project_service = ProjectService(console, config, bq_client)
    result_service = ResultService(console, config, bq_client, infos, results, schemas)
    info_service = InfoService(console, config, bq_client, result_service, infos)
    schema_service = SchemaService(console, config, bq_client)
    job_info = None
    if init:
        initialize(console, auth, project_service)
        ctx.exit()
    elif set_project:
        project_service.set_project()
    elif not os.path.exists(const.BQQ_HOME):
        panel = Panel(
            title="Not initialized, run",
            renderable=Text("bqq --init"),
            expand=False,
            padding=(1, 3),
            border_style=const.request_style,
        )
        console.print(panel)
        ctx.exit()
    elif not config.project:
        panel = Panel(
            title="No project set, run",
            renderable=Text("bqq --set-project"),
            expand=False,
            padding=(1, 3),
            border_style=const.request_style,
        )
        console.print(panel)
        ctx.exit()
    elif file:
        query = file.read()
        job_info = info_service.get_info(yes, query)
    elif sql and os.path.isfile(sql):
        with open(sql, "r") as file:
            query = file.read()
            job_info = info_service.get_info(yes, query)
    elif sql:
        job_info = info_service.get_info(yes, sql)
    elif history:
        job_info = info_service.search_one()
    elif delete:
        infos = info_service.search()
        if infos:
            if Confirm.ask(
                Text("", style=const.darker_style).append(
                    f"Delete selected ({len(infos)})?", style=const.request_style
                ),
                default=True,
                console=console,
            ):
                info_service.delete_infos(infos)
            else:
                console.print(f"Nothing deleted.", style=const.info_style)
            ctx.exit()
    elif clear:
        size = len(infos.get_all())
        if Confirm.ask(
            Text("", style=const.darker_style).append(f"Remove all ({size})?", style=const.request_style),
            default=False,
            console=console,
        ):
            infos.clear()
            results.clear()
            schemas.clear()
            console.print(Text("All removed.", style=const.info_style))
        else:
            console.print(Text("Nothing removed.", style=const.info_style))
        ctx.exit()
    elif schema:
        console.print(schema_service.get_schema())
        ctx.exit()
    elif sync:
        info_service.sync_infos()
    else:
        console.print(ctx.get_help())
        ctx.exit()

    # ---------------------- output -------------------------
    if job_info:
        header = output.get_info_header(job_info)
        console.rule()
        console.print(header)
        console.rule()
        sql = output.get_sql(job_info)
        console.print(sql)
        console.rule()
        result_table = result_service.get_table(job_info)
        if not result_table and job_info.has_result is None:
            if Confirm.ask(
                Text("", style=const.darker_style).append("Download result?", style=const.request_style),
                default=False,
                console=console,
            ):
                result_service.download_result(job_info.job_id)
                job_info = infos.find_by_id(job_info.job_id)  # updated job_info
                result_table = result_service.get_table(job_info)
        if job_info.has_result is False:
            console.print("Query result has expired", style=const.error_style)
            console.rule()
            if Confirm.ask(
                Text("", style=const.darker_style).append("Re-execute query?", style=const.request_style),
                default=False,
                console=console,
            ):
                job_info = info_service.get_info(True, job_info.query)
                result_table = result_service.get_table(job_info)
        if result_table:
            if result_table.width > console.width:
                with console.pager(styles=True):
                    os.environ["LESS"] += " -S"  # enable horizontal scrolling for less
                    console.print(result_table, crop=False)
            else:
                console.print(result_table, crop=False)


def initialize(console: Console, auth: Auth, project_service: ProjectService):
    bqq_home = Prompt.ask(
        Text("", style=const.darker_style).append("Enter bqq home path", style=const.request_style),
        default=const.DEFAULT_BQQ_HOME,
        console=console,
    )
    bqq_results = f"{bqq_home}/results"
    bqq_schemas = f"{bqq_home}/schemas"
    bqq_infos = f"{bqq_home}/infos.json"
    bqq_config = f"{bqq_home}/config.yaml"
    config = Config(bqq_config)

    Path(bqq_home).mkdir(parents=True, exist_ok=True)
    console.print(Text("Created", style=const.info_style).append(f": {bqq_home}", style=const.darker_style))
    Path(bqq_results).mkdir(parents=True, exist_ok=True)
    console.print(Text("Created", style=const.info_style).append(f": {bqq_results}", style=const.darker_style))
    Path(bqq_schemas).mkdir(parents=True, exist_ok=True)
    console.print(Text("Created", style=const.info_style).append(f": {bqq_schemas}", style=const.darker_style))
    Path(bqq_infos).touch()
    console.print(Text("Created", style=const.info_style).append(f": {bqq_infos}", style=const.darker_style))
    config.write_default()
    console.print(Text("Created", style=const.info_style).append(f": {bqq_config}", style=const.darker_style))

    Prompt.ask(
        Text("", style=const.darker_style).append("Login to google account", style=const.request_style),
        choices=None,
        default="Press enter",
        console=console,
    )
    auth.login()

    Prompt.ask(
        Text("", style=const.darker_style).append("Set google project", style=const.request_style),
        choices=None,
        default="Press enter",
        console=console,
    )
    project_service.set_project()

    if bqq_home != const.DEFAULT_BQQ_HOME:
        group = Group(Text(f"export BQQ_HOME={bqq_home}"))
        console.print(
            NewLine(),
            Panel(
                title="Export following to your environment",
                renderable=group,
                expand=False,
                padding=(1, 3),
                border_style=const.request_style,
            ),
        )
