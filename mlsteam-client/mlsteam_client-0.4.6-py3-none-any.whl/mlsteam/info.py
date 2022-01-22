import click
from mlsteam import version
from .api import MyelindlApi, MyelindlApiError


@click.command()
def info():
    try:
        api = MyelindlApi()
        server_ver = api.version()
        click.echo("Version: {}".format(version.__version__))
        click.echo("Server: {}".format(api.host))
        click.echo("Server Version: {}".format(server_ver))
        click.echo("Username: {}".format(api.username))
        click.echo("Data Port: {}".format(api.data_port))
    except MyelindlApiError as e:
        click.echo('Fail due to {}'.format(e))
        raise
