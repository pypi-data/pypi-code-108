import json
import click
from .api import MyelindlApi, MyelindlApiError

@click.command()
@click.argument('container', required=True)
@click.option('--dataset', help='dataset used for container jobs (for container jobs)')
@click.option('--num-gpu', type=click.INT, default=1, help='number of GPU (default: 1)')
@click.option('--port', help='port numbers to be exposed from container')
@click.argument('user-args', nargs=-1, type=click.Path())
def create(container, dataset, num_gpu, port, user_args):
    try:
        api = MyelindlApi()
        result = api.work_create(container, dataset, num_gpu, port, user_args)
        click.echo(result)
    except MyelindlApiError as e:
        click.echo("create work failed, {}".format(e))
        raise


@click.command('list')
def do_list():
    try:
        api = MyelindlApi()
        result = api.work_list()
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    except MyelindlApiError as e:
        click.echo("list work failed, {}".format(e))
        raise


@click.command()
@click.argument('id', required=True)
def delete(_id):
    try:
        api = MyelindlApi()
        api.work_delete(_id)
    except MyelindlApiError as e:
        click.echo("delete a work failed, {}".format(e))
        raise

@click.command()
@click.argument('id', required=True)
def info(_id):
    try:
        api = MyelindlApi()
        result = api.work_info(_id)
        click.echo(json.dumps(result, indent=2, sort_keys=True))
    except MyelindlApiError as e:
        click.echo("list work failed, {}".format(e))
        raise


@click.group(help='Groups of commands to manage works')
def work():
    pass


work.add_command(create)
work.add_command(do_list)
work.add_command(delete)
work.add_command(info)
