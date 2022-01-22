import json
import click
from .api import MyelindlApi, MyelindlApiError

@click.command()
@click.argument('id', required=True)
def download(_id):
    try:
        api = MyelindlApi()
        result = api.checkpoint_download(_id)
        click.echo(result)
    except MyelindlApiError as e:
        click.echo("download checkpoint failed, {}".format(e))
        raise


@click.command('list')
def do_list():
    try:
        api = MyelindlApi()
        result = api.checkpoint_list()
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    except MyelindlApiError as e:
        click.echo("list checkpoint failed, {}".format(e))
        raise


@click.command()
@click.argument('id', required=True)
def delete(_id):
    try:
        api = MyelindlApi()
        api.checkpoint_delete(_id)
    except MyelindlApiError as e:
        click.echo("delete a checkpoint failed, {}".format(e))
        raise


@click.command()
@click.argument('id', required=True)
def info(_id):
    try:
        api = MyelindlApi()
        result=api.checkpoint_info(_id)
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    except MyelindlApiError as e:
        click.echo("show checkpoint info failed, {}".format(e))
        raise


@click.group(help='Groups of commands to manage checkpoints')
def checkpoint():
    pass


checkpoint.add_command(download)
checkpoint.add_command(do_list)
checkpoint.add_command(delete)
checkpoint.add_command(info)
