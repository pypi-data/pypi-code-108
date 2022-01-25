import json
import logging
import os
import sys
from typing import Any

import click

from anyscale.cli_logger import BlockLogger
from anyscale.commands.anyscale_api.api_commands import anyscale_api
from anyscale.commands.cloud_commands import cloud_cli
from anyscale.commands.cluster_commands import cluster_cli
from anyscale.commands.cluster_compute_commands import cluster_compute_cli
from anyscale.commands.cluster_env_commands import cluster_env_cli
from anyscale.commands.config_commands import config_cli
from anyscale.commands.exec_commands import anyscale_exec
from anyscale.commands.job_commands import job_cli
from anyscale.commands.list_commands import list_cli
from anyscale.commands.migrate_commands import migrate_cli
from anyscale.commands.project_commands import (
    anyscale_clone,
    anyscale_init,
    project_cli,
)
from anyscale.commands.run_commands import anyscale_kill_job, anyscale_run
from anyscale.commands.service_commands import service_cli
from anyscale.commands.session_commands import (
    anyscale_autopush,
    anyscale_autosync,
    anyscale_fork,
    anyscale_pull,
    anyscale_push,
    anyscale_ssh,
    anyscale_start,
    anyscale_stop,
    anyscale_up,
)
from anyscale.commands.session_commands_hidden import session_cli
import anyscale.conf
from anyscale.util import init_sentry


logger = logging.getLogger(__file__)
logging.getLogger("botocore").setLevel(logging.CRITICAL)

log = BlockLogger()  # CLI Logger

if anyscale.conf.AWS_PROFILE is not None:
    logger.info("Using AWS profile %s", anyscale.conf.AWS_PROFILE)
    os.environ["AWS_PROFILE"] = anyscale.conf.AWS_PROFILE


class AliasedGroup(click.Group):
    # This is from https://stackoverflow.com/questions/46641928/python-click-multiple-command-names
    def get_command(self, ctx: Any, cmd_name: str) -> Any:
        try:
            cmd_name = ALIASES[cmd_name].name
        except KeyError:
            pass
        return super().get_command(ctx, cmd_name)


@click.group(
    invoke_without_command=True,
    no_args_is_help=True,
    cls=AliasedGroup,
    context_settings=dict(help_option_names=["-h", "--help"]),
)
@click.option(
    "--version",
    "-v",
    "version_flag",
    is_flag=True,
    default=False,
    help="Current anyscale version.",
)
@click.option(
    "--json",
    "show_json",
    is_flag=True,
    default=False,
    help="Return output as json, for use with --version.",
)
@click.pass_context
def cli(ctx: Any, version_flag: bool, show_json: bool) -> None:
    # Use anyscale vendored Ray for the CLI:
    sys.path.insert(0, anyscale.ANYSCALE_RAY_DIR)
    if (
        (ctx.invoked_subcommand not in {"help", "version"})
        and ("--help" not in sys.argv)
        and ("-h" not in sys.argv)
    ):
        init_sentry(ctx.invoked_subcommand)

    if version_flag:
        ctx.invoke(version_cli, show_json=show_json)


@click.command(name="version", help="Display version of the anyscale CLI.")
@click.option(
    "--json", "show_json", is_flag=True, default=False, help="Return output as json."
)
def version_cli(show_json: bool) -> None:
    if show_json:
        print(json.dumps({"version": anyscale.__version__}))
    else:
        log.info(anyscale.__version__)


@cli.command(
    name="help", help="Display help documentation for anyscale CLI.", hidden=True
)
@click.pass_context
def anyscale_help(ctx: Any) -> None:
    print(ctx.parent.get_help())


cli.add_command(session_cli)
cli.add_command(cloud_cli)
cli.add_command(config_cli)
cli.add_command(migrate_cli)
cli.add_command(project_cli)
cli.add_command(version_cli)
cli.add_command(list_cli)
cli.add_command(cluster_env_cli)
cli.add_command(job_cli)
cli.add_command(service_cli)
cli.add_command(cluster_cli)

cli.add_command(anyscale_init)
cli.add_command(anyscale_up)
cli.add_command(anyscale_stop)
cli.add_command(anyscale_autosync)
cli.add_command(anyscale_autopush)
cli.add_command(anyscale_fork)
cli.add_command(anyscale_clone)
cli.add_command(anyscale_ssh)
cli.add_command(anyscale_start)
cli.add_command(anyscale_exec)
cli.add_command(anyscale_run)
cli.add_command(anyscale_kill_job)
cli.add_command(anyscale_pull)
cli.add_command(anyscale_push)
cli.add_command(anyscale_help)
cli.add_command(cluster_compute_cli)

# Commands to interact with the Anyscale API
cli.add_command(anyscale_api)

ALIASES = {"h": anyscale_help}


def main() -> Any:
    return cli()


if __name__ == "__main__":
    main()
