from typing import Optional

import click

from anyscale.cli_logger import BlockLogger
from anyscale.commands.util import NotRequiredIf
from anyscale.controllers.project_controller import ProjectController
from anyscale.project import validate_project_name
from anyscale.util import validate_non_negative_arg


log = BlockLogger()


@click.group(
    "project",
    short_help="Manage projects on Anyscale.",
    help="Manages projects on Anyscale. A project can be used to organize a collection of jobs.",
)
def project_cli() -> None:
    pass


@project_cli.command(
    name="list",
    short_help="List projects for which you have access.",
    help="List projects for which you have access. By default, only projects created by you are listed.",
)
@click.option(
    "--name", "-n", help="List information for a particular project.", type=str
)
@click.option("--json", help="Format output as JSON.", is_flag=True)
@click.option(
    "--any-creator", "-a", help="List projects created by any user.", is_flag=True
)
@click.option(
    "--max-items",
    required=False,
    default=20,
    type=int,
    help="Max items to show in list.",
    callback=validate_non_negative_arg,
)
def list(name: str, json: bool, any_creator: bool, max_items: int) -> None:
    project_controller = ProjectController()
    project_controller.list(name, json, any_creator, max_items)


@click.command(
    name="clone",
    short_help="DEPRECATED: Clone a project that exists on anyscale, to your local machine.",
    help="""
[DEPRECATED]

Clone a project that exists on anyscale, to your local machine.
This command will create a new folder on your local machine inside of
the current working directory and download the most recent snapshot.

This is frequently used with anyscale push or anyscale pull to download, make
changes, then upload those changes to a currently running cluster.""",
    hidden=True,
)
@click.argument("project-name", required=True)
@click.option(
    "--owner",
    help="Username or email of the user who owns the project. Defaults to the current user.",
    required=False,
)
def anyscale_clone(project_name: str, owner: Optional[str]) -> None:
    project_controller = ProjectController()
    project_controller.clone(project_name, owner=owner)


def _validate_project_name(ctx, param, value) -> str:
    if value and not validate_project_name(value):
        raise click.BadParameter(
            '"{}" contains spaces. Please enter a project name without spaces'.format(
                value
            )
        )

    return value


def _default_project_name() -> str:
    import os

    cur_dir = os.getcwd()
    return os.path.basename(cur_dir)


@click.command(
    name="init",
    help=(
        "[DEPRECATED] Create a new project or attach this directory to an existing project."
    ),
    hidden=True,
)
@click.option(
    "--project-id",
    help="Project id for an existing project you wish to attach to.",
    required=False,
    prompt=False,
)
@click.option(
    "--name",
    help="Project name.",
    cls=NotRequiredIf,
    not_required_if="project_id",
    callback=_validate_project_name,
    prompt=True,
    default=_default_project_name(),
)
@click.option(
    "--config",
    help="[DEPRECATED] Path to autoscaler yaml. Created by default.",
    type=click.Path(exists=True),
    required=False,
)
@click.option(
    "--requirements",
    help="[DEPRECATED] Path to requirements.txt. Created by default.",
    required=False,
)
def anyscale_init(
    project_id: Optional[str],
    name: Optional[str],
    config: Optional[str],
    requirements: Optional[str],
) -> None:
    log.warning(
        "`anyscale init` has been deprecated. Please use `anyscale project init` "
        "to create or attach to a project from this directory."
    )
    if (project_id and name) or not (project_id or name):
        raise click.BadArgumentUsage(
            "Only one of project_id and name must be provided."
        )

    project_controller = ProjectController()
    project_controller.init(project_id, name, config, requirements)


@project_cli.command(
    name="init",
    help="Create a new project or attach this directory to an existing project.",
)
@click.option(
    "--project-id",
    "--id",
    help="Project id for an existing project you wish to attach to.",
    required=False,
    prompt=False,
)
@click.option(
    "--name",
    "-n",
    help="Project name.",
    cls=NotRequiredIf,
    not_required_if="project_id",
    callback=_validate_project_name,
    prompt=True,
    default=_default_project_name(),
)
def init(project_id: Optional[str], name: Optional[str],) -> None:
    if (project_id and name) or not (project_id or name):
        raise click.BadArgumentUsage(
            "Only one of --project-id and --name must be provided."
        )

    project_controller = ProjectController()
    project_controller.init(project_id, name, None, None)
