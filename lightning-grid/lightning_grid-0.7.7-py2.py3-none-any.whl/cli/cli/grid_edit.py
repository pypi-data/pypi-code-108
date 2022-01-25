import json

import click

from grid.cli import rich_click
from grid.cli.cli.utilities import create_openapi_object, string2dict
from grid.openapi import Body
from grid.openapi.api import cluster_service_api
from grid.sdk.client import create_swagger_client


@rich_click.group()
def edit() -> None:
    """Edits a resource"""
    pass


@edit.command()
@rich_click.argument('cluster', type=str)
def cluster(cluster: str):
    """Edit existing cluster"""
    api_client = create_swagger_client()
    cluster_api = cluster_service_api.ClusterServiceApi(api_client)
    resp = cluster_api.cluster_service_get_cluster(cluster)
    spec_str = click.edit(json.dumps(resp.spec.to_dict(), indent=4))
    new_spec = resp.spec
    if spec_str is not None:
        new_spec = create_openapi_object(string2dict(spec_str), resp.spec)
    if new_spec == resp.spec:
        click.echo("cluster unchanged")
        return
    body = Body(name=cluster, spec=new_spec)
    update_resp = cluster_api.cluster_service_update_cluster(id=cluster, body=body)
    click.echo(update_resp.to_str())
