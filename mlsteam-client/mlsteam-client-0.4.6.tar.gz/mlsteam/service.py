import json
import click
from .api import MyelindlApi, MyelindlApiError

@click.command()
@click.argument('id', required=True)
def create(_id):
    try:
        api = MyelindlApi()
        result = api.service_create(_id)
        click.echo(result)
    except MyelindlApiError as e:
        click.echo("create service failed, {}".format(e))
        raise


@click.command('list')
def do_list():
    try:
        api = MyelindlApi()
        result = api.service_list()
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    except MyelindlApiError as e:
        click.echo("list service failed, {}".format(e))
        raise


@click.command()
@click.argument('id', required=True)
def delete(_id):
    try:
        api = MyelindlApi()
        api.service_delete(_id)
    except MyelindlApiError as e:
        click.echo("delete a service failed, {}".format(e))
        raise


@click.group(help='Groups of commands to manage services')
def service():
    pass


service.add_command(create)
service.add_command(do_list)
service.add_command(delete)
