import json
import sys
from typing import List

import click
import yaml
from pydantic import UUID4, BaseModel

from tktl.cli.common import (
    LOG,
    ClickGroup,
    filter_deploy_shared_options,
    filter_repo_shared_options,
    get_cmd_shared_options,
    to_uuid,
)
from tktl.commands import deployments as deployments_commands
from tktl.core.config import settings
from tktl.core.schemas.repository import Endpoint
from tktl.core.schemas.utils import get_table_from_list_of_schemas
from tktl.core.t import EndpointKinds
from tktl.login import validate_decorator


@click.group("get", help="Get resources", cls=ClickGroup, **settings.HELP_COLORS_DICT)
def get():
    pass


@get.command("repositories", help="Get repository resources")
@get_cmd_shared_options
@filter_repo_shared_options
@validate_decorator
def get_repositories(
    repo: str, owner: str, all_resources: bool, output: str, full: bool,
):
    command = deployments_commands.GetRepositories()
    result = command.execute(
        repository_name=repo, repository_owner=owner, return_all=all_resources,
    )
    keys = None
    if not full:
        keys = ["ID", "FULL NAME", "DEPLOYMENTS"]
        result = list(set(result))
    return produce_output(resources=result, keys=keys, maxwidth=200, output_kind=output)


@get.command("deployments", help="Get deployment resources")
@click.argument("repository_id", required=False, callback=to_uuid)
@get_cmd_shared_options
@filter_deploy_shared_options
@filter_repo_shared_options
@validate_decorator
def get_deployment_by_repo_id(
    output: str,
    repository_id: UUID4 = None,
    repo: str = None,
    owner: str = None,
    commit: str = None,
    branch: str = None,
    status: str = None,
    all_resources: bool = False,
    full: bool = None,
):
    command = deployments_commands.GetDeployments()
    if output == "stdout" and not repository_id:
        LOG.warning(
            "Fetching multiple deployments, this can take a few seconds. "
            "Pass a repository_id or branch/commit if you only want the deployments for a specific repository"
        )

    result = command.execute(
        repository_id=repository_id,
        repository_name=repo,
        repository_owner=owner,
        git_hash=commit,
        branch_name=branch,
        status_name=status,
        return_all=all_resources,
    )
    keys = ["ID", "BRANCH", "COMMIT", "STATUS", "ENDPOINTS"] if not full else None
    return produce_output(resources=result, keys=keys, maxwidth=350, output_kind=output)


@get.command("endpoints", help="Get endpoint resources")
@click.argument("deployment_id", required=False, callback=to_uuid)
@click.option("-e", "--endpoint", help="Endpoint name")
@click.option(
    "-k",
    "--endpoint-kind",
    help="Endpoint kind",
    type=click.Choice(EndpointKinds.list()),
)
@get_cmd_shared_options
@filter_deploy_shared_options
@filter_repo_shared_options
@validate_decorator
def get_endpoint_by_deployment_id(
    deployment_id: UUID4,
    repo: str,
    owner: str,
    commit: str,
    branch: str,
    status: str,
    endpoint_kind,
    endpoint: str,
    all_resources: bool,
    output: str,
    full: bool = True,
):
    command = deployments_commands.GetEndpoints()
    if output == "stdout" and not deployment_id:
        LOG.warning(
            "Fetching multiple endpoints, this can take a few seconds. "
            "Pass a deployment_id if you only want the endpoints for a specific deployment"
        )

    result = command.execute(
        deployment_id=deployment_id,
        endpoint_name=endpoint,
        endpoint_kind=endpoint_kind,
        repository_name=repo,
        repository_owner=owner,
        git_hash=commit,
        branch_name=branch,
        status_name=status,
        return_all=all_resources,
    )
    return produce_output(resources=result, output_kind=output, keys=None, maxwidth=130)


class GenericResourceList(BaseModel):
    __root__: List


def produce_output(
    resources: List[Endpoint],
    output_kind: str,
    keys: List[str] = None,
    maxwidth: int = None,
):
    if not resources:
        LOG.error("No resources found")
        sys.exit(1)
    if output_kind == "stdout":
        table = get_table_from_list_of_schemas(resources, maxwidth=maxwidth, keys=keys)
        LOG.log(table)
    elif output_kind == "json":
        LOG.log(GenericResourceList.parse_obj(resources).json())
    elif output_kind == "yaml":
        LOG.log(yaml.dump_all([json.loads(r.json()) for r in resources]))
