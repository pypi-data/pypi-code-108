import click
from rich import print as rprint
from pathlib import Path

from pydragonfly import DragonflyException, TParams
from .._utils import (
    ClickContext,
    json_flag_option,
    get_status_text,
    get_success_text,
    add_options,
)
from ._renderables import (
    _display_single_analysis,
    _paginate_table,
    _generate_analysis_table,
)


@click.group("analysis")
def analysis():
    """
    Analysis Management\n
    >>> [API] https://dragonfly.certego.net/api/analysis\n
    >>> [GUI] https://dragonfly.certego.net/history/analysis
    """


@analysis.command("list", help="List all analysis")
@click.option(
    "--status",
    type=click.Choice(
        [
            "QUEUED",
            "PENDING",
            "RUNNING",
            "ANALYZED",
            "FAILED",
            "REVOKED",
        ],
        case_sensitive=False,
    ),
    show_choices=True,
    help="Filter against status",
)
@click.option(
    "--evaluation",
    type=click.Choice(
        [
            "CLEAN",
            "SUSPICIOUS",
            "MALICIOUS",
        ],
        case_sensitive=False,
    ),
    show_choices=True,
    help="Filter against evaluation",
)
@add_options(json_flag_option)
@click.pass_context
def analysis_list(ctx: ClickContext, status: str, evaluation: str, as_json: bool):
    ctx.obj._logger.info("Requesting list of analysis..")
    ctx.obj._logger.info(f"[+] GUI: {ctx.obj._server_url}/history/analysis")
    params = TParams(ordering=["-created_at"])
    if status:
        params["status"] = status.upper()
    if evaluation:
        params["evaluation"] = evaluation.upper()
    try:
        if as_json:
            response = ctx.obj.Analysis.list(params=params)
            rprint(response.data)
        else:
            generator = ctx.obj.Analysis.auto_paging_iter(params=params)
            _paginate_table(generator, _generate_analysis_table)
    except DragonflyException as exc:
        ctx.obj._logger.fatal(str(exc))


@analysis.command("retrieve", help="Retrieve analysis info and result")
@click.argument("analysis_id", type=int)
@add_options(json_flag_option)
@click.pass_context
def analysis_retrieve(ctx: ClickContext, analysis_id: int, as_json: bool):
    ctx.obj._logger.info(f"Requesting analysis [underline blue]#{analysis_id}[/]..")
    try:
        response = ctx.obj.Analysis.retrieve(
            object_id=analysis_id,
            params=TParams(
                expand=["sample"],
                omit=[
                    "sample.file_deleted",
                    "sample.sections",
                    "sample.flags",
                    "sample.dlls_imported",
                    "sample.entry_points",
                    "sample.user",
                    "sample.file_version_info",
                ],
            ),
        )
        if as_json:
            rprint(response.data)
        else:
            _display_single_analysis(response.data)
    except DragonflyException as exc:
        ctx.obj._logger.fatal(str(exc))


@analysis.command("create", help="Submit a sample for analysis")
@click.argument("filepath", type=click.Path(exists=True, resolve_path=True))
@click.option(
    "-pl",
    "--profiles-list",
    type=str,
    default="",
    help="Comma separated list of profile indices",
)
@click.option(
    "-os",
    "--operating-system",
    type=click.Choice(["automatic", "WINDOWS", "LINUX"], case_sensitive=False),
    default="automatic",
    show_choices=True,
    show_default=True,
    help="Operating system for profile",
)
@click.option(
    "-al",
    "--arguments-list",
    type=str,
    default="",
    help="Comma separated list of extra command line arguments for the emulator",
)
@click.option(
    "-dl",
    "--dll-entrypoints",
    type=str,
    default="",
    help="""Comma separated list of DLL entrypoints.
    Supports only DLL sample. Default: all entrypoints.
    """,
)
@click.option(
    "-a",
    "--allow-actions",
    is_flag=True,
    show_default=True,
    help="Run actions when a rule matches (coming soon)",
)
@click.option(
    "-r",
    "--root",
    is_flag=True,
    show_default=True,
    help="Emulate with root permissions",
)
@click.option(
    "-p",
    "--private",
    is_flag=True,
    show_default=True,
    help="""
    Mark the analysis as private so it's accessible
    to you and members within your organization only
    """,
)
@click.pass_context
def analysis_create(
    ctx: ClickContext,
    filepath: str,
    profiles_list: str,
    operating_system: str,
    arguments_list: str,
    dll_entrypoints: str,
    allow_actions: bool,
    root: bool,
    private: bool,
):
    fpath = Path(filepath)
    profiles = profiles_list.split(",") if len(profiles_list) else []
    arguments = arguments_list.split(",") if len(arguments_list) else []
    dll_entrypoints = dll_entrypoints.split(",") if len(dll_entrypoints) else []
    try:
        ctx.obj._logger.info(
            f"""
Requesting analysis...
    file: [blue]{fpath.name}[/]
    (   profiles: [i green]{profiles}[/],
        os: [i green]{operating_system}[/],
        private: [i green]{private}[/]
    )
            """
        )
        response = ctx.obj.Analysis.create(
            data=ctx.obj.Analysis.CreateAnalysisRequestBody(
                profiles=profiles,
                os=operating_system
                if operating_system in ["WINDOWS", "LINUX"]
                else None,
                arguments=arguments,
                dll_entrypoints=dll_entrypoints,
                allow_actions=allow_actions,
                root=root,
                private=private,
            ),
            sample_name=fpath.name,
            sample_buffer=fpath.read_bytes(),
        )
        analysis_id = response.data["id"]
        gui_url = response.data["gui_url"]
        status = response.data["status"]
        filename = response.data["sample"]["filename"]
        sha256 = response.data["sample"]["sha256"]
        ctx.obj._logger.info(
            f"""
Success {get_success_text("True", as_text=False)}...
    [+] ID: {analysis_id}
    [+] File/SHA256: [cyan]{filename} ({sha256})[/]
    [+] Status: {get_status_text(status, as_text=False)}
    [+] URL: {gui_url}
            """
        )

    except DragonflyException as exc:
        ctx.obj._logger.fatal(str(exc))
