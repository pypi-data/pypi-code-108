import click

from spell.api import models
from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.utils import (
    prettify_timespan,
    tabulate_rows,
    format_multiline_table_output,
    format_multiline_text_to_table,
)


@click.command(
    name="info",
    short_help="Describes a run. Displays info such as start and end time as well as "
    "run parameters such as apts, pips, and mounts.",
)
@click.argument("run_id")
@click.pass_context
def info(ctx, run_id):
    """
    Displays information about a run including the start and end time as well run parameters such as
    apts, pips, and mounts.
    """

    run = None
    with api_client_exception_handler():
        client = ctx.obj["client"]
        run = client.get_run(run_id)
        if isinstance(run, models.Error):
            raise ExitException(run.status)

    lines = []
    if run.project:
        lines.append(("Project", run.project.name))
    if run.workspace:
        lines.append(("Repository", run.workspace.name))
    if run.git_commit_hash:
        lines.append(("Git Commit", run.git_commit_hash))
    exit_code_string = f" ({run.user_exit_code})" if run.user_exit_code is not None else ""
    lines.append(("Status", f"{run.status}{exit_code_string}"))
    if run.resumed_as_run:
        lines.append(("Resumed As Run", run.resumed_as_run))
    if run.resumed_from_run:
        lines.append(("Resumed As Run", run.resumed_from_run))
    lines.append(("Command", run.command))
    lines.append(("Creator", run.creator.user_name))
    lines.append(("Machine Type", run.gpu))
    if run.docker_image:
        lines.append(("Docker Image", run.docker_image.split("@")[0]))
    if run.github_url:
        lines.append(("GitHub URL", run.github_url))
    if run.started_at is not None:
        lines.append(("Start Time", "{:%Y-%m-%d %H:%M:%S}".format(run.started_at)))
    if run.ended_at is not None:
        lines.append(("End Time", "{:%Y-%m-%d %H:%M:%S}".format(run.ended_at)))
        if run.started_at is not None:
            lines.append(("Duration", prettify_timespan(run.started_at, run.ended_at)))

    if run.labels:
        lines.extend(format_multiline_table_output("Labels", run.labels, lambda label: label["name"]))

    if run.attached_resources:
        lines.extend(
            format_multiline_table_output(
                "Mounts", run.attached_resources, lambda resource, path: f"{resource} at {path}"
            )
        )

    if run.environment_vars:
        lines.extend(format_multiline_table_output("Environment Vars", run.environment_vars))

    if run.pip_env_packages:
        lines.extend(format_multiline_table_output("Python Environment", run.pip_env_packages))

    if run.requirements_file:
        lines.extend(format_multiline_text_to_table("Requirements File", run.requirements_file))
    if run.pip_packages:
        lines.extend(format_multiline_table_output("Pip Packages", run.pip_packages))

    if run.apt_packages:
        lines.extend(format_multiline_table_output("Apt Packages", run.apt_packages))

    if run.conda_env_file:
        lines.extend(format_multiline_text_to_table("Conda Env File", run.conda_env_file))

    if run.hyper_params:
        lines.extend(format_multiline_table_output("Hyperparameters", run.hyper_params))

    tabulate_rows(lines)
