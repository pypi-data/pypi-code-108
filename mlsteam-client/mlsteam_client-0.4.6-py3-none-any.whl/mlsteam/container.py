import click
from mlsteam.api import MyelindlApi, MyelindlApiError


@click.command('list')
def do_list():
    try:
        api = MyelindlApi()
        result = api.image_list()
        longest = 20
        if result:
            longest = max(len(x['tag']) for x in result)
        if longest < 20:
            longest = 20
        template = '| {:>10} | {:>%d} |'% longest
        header = template.format('id', 'tag')
        click.echo('=' * len(header))
        click.echo(header)
        click.echo('=' * len(header))
        for img in result:
            line = template.format(img['id'], img['tag'])
            click.echo(line)
        click.echo('=' * len(header))
    except MyelindlApiError as e:
        click.echo(str(e))
        raise


@click.command()
@click.option('--id', required=True, help="image id")
def delete(_id):
    try:
        api = MyelindlApi()
        result = api.image_delete(_id)
        click.echo(result)
    except MyelindlApiError as e:
        click.echo(str(e))
        raise


@click.command()
@click.option('--tag', required=True, help="image tag")
def pull(tag):
    try:
        api = MyelindlApi()
        result = api.image_pull(tag)
        click.echo(result)
    except MyelindlApiError as e:
        click.echo(str(e))
        raise


@click.group(help='Group of commands to manage container images')
def image():
    pass

image.add_command(do_list)
image.add_command(delete)
image.add_command(pull)


@click.group(help='Groups of commands to manage container')
def container():
    pass

container.add_command(image)
