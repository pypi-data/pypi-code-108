import shutil

import click

from spell.cli.exceptions import api_client_exception_handler
from spell.cli.utils import prettify_time, tabulate_rows, truncate_string, command, fetch_project
from spell.cli.log import logger


# display order of columns
COLUMNS = [
    "id",
    "repo_name",
    "command",
    "pretty_status",
    "creator_name",
]
VERBOSE_COLUMNS = [
    "id",
    "repo_name",
    "command",
    "git_commit_hash",
    "pretty_status",
    "creator_name",
    "gpu",
    "description",
]

# title lookup
TITLES = {
    "id": "ID",
    "repo_name": "REPOSITORY",
    "command": "COMMAND",
    "git_commit_hash": "COMMIT",
    "pretty_status": "STATUS",
    "creator_name": "CREATOR",
    "gpu": "MACHINE",
    "description": "DESCRIPTION",
    "labels": "LABELS",
    "distributed": "DISTRIBUTED",
}

status_names = {
    "user_requested": "Requested",
    "machine_requested": "Queued",
    "build_failed": "Build Failed",
    "mount_failed": "Mount Failed",
}


COMMIT_DISPLAY_LENGTH = 8
COMMAND_DISPLAY_LENGTH = 25
BASE_PS_WIDTH = 116
MIN_DESCRIPTION_WIDTH = 12


# prettify_status returns a nice human readable status for display to the user
def prettify_status(run, verbose=False):
    status = status_names.get(run.status, run.status).title()
    if run.user_exit_code is not None:
        status += f" ({run.user_exit_code})"
    if verbose and run.started_at is not None and run.ended_at is None:
        status += f" [{prettify_time(run.started_at, elapsed=True)}]"
    elif verbose and run.ended_at is not None:
        status += f" -- {prettify_time(run.ended_at)}"
    if verbose and run.status in ("user_requested", "machine_requested"):
        return click.style(status + f" -- {prettify_time(run.created_at)}", fg="yellow")
    elif run.status in (
        "building",
        "mounting",
        "running",
        "stopping",
        "saving",
        "pushing",
        "killing",
    ):
        return click.style("*" + status, fg="green")
    return status


@command(name="ps", short_help="Display run statuses")
@click.option("-n", "--number", default=50, type=int, help="The number of runs to display")
@click.option("--raw", is_flag=True, help="Display output in raw format", hidden=True)
@click.option("--trunc/--no-trunc", default=True, help="Truncate command output")
@click.option("-r", "--repository", default=None, help="Repository name to filter runs by")
@click.option(
    "-l",
    "--label",
    "labels",
    multiple=True,
    help="Label name to filter runs by. Multiple usages will return runs with ANY of the input labels",
)
@click.option("-p", "--project", "project", help="Name of project to list runs from")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Include extra columns such as git commit hash and description",
)
@click.option("--include-jupyter", is_flag=True, help="Include jupyter workspace runs", hidden=True)
@click.pass_context
def ps(
    ctx,
    number,
    raw,
    trunc,
    repository,
    labels,
    project,
    verbose,
    include_jupyter,
):
    """
    Display all user runs and their details

    Displays information about all of the user's active and historical runs,
    displayed oldest to newest. It can be used to keep track of current active
    runs or find a historical run.
    """
    # retrieve runs from API
    with api_client_exception_handler():
        logger.info("Retrieving runs from Spell")
        client = ctx.obj["client"]

        project_id = None
        if project:
            proj = fetch_project(client, project)
            project_id = proj.id

        if repository is None:
            runs = client.list_runs(
                number=number,
                include_jupyter=include_jupyter,
                labels=labels,
                project=project_id,
                show_uncategorized=project_id is None,
            )
        else:
            repos = client.get_workspaces_by_name(repository)
            if len(repos) == 0:
                logger.error("No repository found named %s", repository)
                return
            runs = client.list_runs(
                [str(repo.id) for repo in repos],
                number=number,
                include_jupyter=include_jupyter,
                labels=labels,
                project=project_id,
                show_uncategorized=project_id is None,
            )
        # Display runs in ascending order
        runs.reverse()

    screen_w = shutil.get_terminal_size()[0]

    # prettify attrs for output
    utf8 = ctx.obj["utf8"]
    distributedExists = False
    labelsExist = False
    for run in runs:
        run.id = str(run.id)
        if trunc:
            run.command = truncate_string(run.command, COMMAND_DISPLAY_LENGTH, utf8=utf8)
        run.repo_name = run.workspace.name if run.workspace else ""
        run.git_commit_hash = run.git_commit_hash[:COMMIT_DISPLAY_LENGTH]
        run.pretty_status = prettify_status(run, verbose=verbose)
        run.creator_name = run.creator.user_name
        run.pretty_created_at = prettify_time(run.created_at)
        run.description = truncate_string(
            run.description, max(screen_w - BASE_PS_WIDTH, MIN_DESCRIPTION_WIDTH), utf8=utf8
        )
        if run.labels:
            labelsExist = True
            run.labels = ", ".join((lbl["name"] for lbl in run.labels))
        else:
            run.labels = ""
        if run.distributed:
            distributedExists = True
            run.distributed = str(run.distributed)
        else:
            run.distributed = ""

    columns = VERBOSE_COLUMNS if verbose else COLUMNS
    if labelsExist and verbose:
        # Put 'labels' after 'creator' if verbose and labels exist
        columns.insert(6, "labels")
    if distributedExists:
        columns.append("distributed")
    tabulate_rows(runs, headers=[TITLES[col] for col in columns], columns=columns, raw=raw)
