import click
from taktile_client.config import collect_api_key
from taktile_types.enums.instance import ServiceType

from tktl.cli.common import ClickCommand
from tktl.commands.health import GetGrpcHealthCommand, GetRestHealthCommand
from tktl.core.config import settings
from tktl.core.exceptions import APIClientException, TaktileSdkError
from tktl.core.loggers import LOG
from tktl.login import login, logout


@click.command(
    "health",
    help="Health check your endpoints",
    cls=ClickCommand,
    **settings.HELP_COLORS_DICT
)
@click.option("-r", "--repo", help="Repository owner & name: owner/repo-name")
@click.option("-b", "--branch", help="Branch name")
@click.option(
    "-s",
    "--service",
    help="Service kind",
    type=click.Choice([ServiceType.REST, ServiceType.GRPC]),
    default=ServiceType.REST,
)
@click.option(
    "-l", "--local", help="Run against local endpoint", is_flag=True, default=False
)
@click.pass_context
def health(
    ctx, repo: str, branch: str, service: str = ServiceType.REST, local: bool = False,
):
    if not local:
        if not repo and not branch:
            return click.echo(health.get_help(ctx=ctx))
        if (repo and not branch) or (branch and not repo):
            LOG.error("If not running locally, must set branch and repo name")
            return

    api_key = collect_api_key()
    if local and not api_key:
        login(api_key="NOT SET")
    command = (
        GetRestHealthCommand(
            repository=repo, branch_name=branch, local=local, skip_auth=True
        )
        if service == ServiceType.REST
        else GetGrpcHealthCommand(
            repository=repo, branch_name=branch, local=local, skip_auth=True
        )
    )
    try:
        command.execute()
    except APIClientException:
        exit(1)
    except TaktileSdkError as e:
        LOG.error(str(e))
    finally:
        if not api_key:
            logout()
