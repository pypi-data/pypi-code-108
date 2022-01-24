import click
from pydantic import UUID4

from tktl.cli.common import ClickGroup, to_uuid
from tktl.commands.deployments import DeleteDeployment
from tktl.core.config import settings
from tktl.core.exceptions import APIClientException
from tktl.core.loggers import LOG
from tktl.login import validate_decorator


@click.group(
    "delete", help="Delete resources", cls=ClickGroup, **settings.HELP_COLORS_DICT
)
def delete():
    pass


@delete.command("deployment", help="Manage deployments")
@click.argument("deployment_id", required=True, callback=to_uuid)
@validate_decorator
def delete_deployment_by_id(deployment_id: UUID4):
    inp = click.prompt(
        f"Deleting deployment with id {deployment_id}. Do you wish to continue? [y (or press enter)/n]",
        default="y",
        show_choices=False,
        show_default=False,
    )
    if inp != "y":
        LOG.error("Safe choice!")
    command = DeleteDeployment()
    try:
        response = command.execute(deployment_id=deployment_id)
    except APIClientException:
        LOG.error("Only super users have access to this method at this time")
        return
    LOG.warning(f"Deployment with id: {response.id}")
    return response
