import json
from datetime import datetime
import click
from .api import MyelindlApi, MyelindlApiError


@click.command()
@click.argument('name', required=True)
@click.argument('dataset', required=True)
def create(name, dataset):
    try:
        if dataset.startswith('bk/'):
            click.echo("no need 'bk/' prefix for dataset.")
            return
        api = MyelindlApi()
        result = api.project_create(name, dataset)

        click.echo('{}'.format(result['id']))
    except MyelindlApiError as e:
        click.echo("new project failed, {}".format(e))
        raise


@click.command('list')
@click.option('--json', 'is_json', default=False, help="return json format output")
def do_list(is_json):
    try:
        api = MyelindlApi()
        result = api.project_list()
        longest = 10
        if result:
            longest = max(len(p['name']) for p in result)
        if longest < 10:
            longest = 10
        if is_json:
            click.echo(json.dumps(result, indent=2, sort_keys=True))
            return
        template = '| {:>8} | {:>%d} | {:>8} | {:>21} |'% longest
        header = template.format('id', 'name', 'user', 'create time')
        click.echo('=' * len(header))
        click.echo(header)
        click.echo('=' * len(header))
        for proj in result:
            line = template.format(proj['id'],
                                   proj['name'],
                                   proj['username'],
                                   datetime.fromtimestamp(proj['create_time']).strftime("%Y %b %d, %H:%M:%S"))
            click.echo(line)
        click.echo('=' * len(header))
    except MyelindlApiError as e:
        click.echo("list project failed, {}".format(e))
        raise


@click.command()
@click.option('--id', required=True, help="id of the project")
def delete(_id):
    try:
        api = MyelindlApi()
        api.project_delete(_id)
    except MyelindlApiError as e:
        click.echo("delete a project failed, {}".format(e))
        raise


@click.command()
@click.option('id', '--id', required=True, help='id')
def info(_id):
    try:
        api = MyelindlApi()
        result=api.project_get_info(_id)

        template = '| {:>11} | {:>40}|'
        header = template.format('Field', 'Value')
        click.echo('=' * len(header))
        click.echo(header)
        click.echo('=' * len(header))

        for k, v in result['info'].items():
            line = template.format(k, v)
            click.echo(line)
        click.echo('='* len(header))
    except MyelindlApiError as e:
        click.echo("show project info failed, {}".format(e))
        raise


@click.group(help='Groups of commands to manage project')
def project():
    pass


project.add_command(create)
project.add_command(do_list)
project.add_command(delete)
project.add_command(info)
