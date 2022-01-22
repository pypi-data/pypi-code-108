import os
import click
from .api import MyelindlApi, MyelindlApiError


@click.command()
@click.option('--address', required=True, help="server address")
@click.option('--username', required=False, help="username")
@click.option('--data-port', required=False, default=5000, help="data transfer port")
def login(address, username, data_port):
    try:
        if username is None:
            username = click.prompt('Please enter username')
        password = click.prompt('Please enter password', hide_input=True)
        api = MyelindlApi(address, username, data_port)
        api.login(password)
        minio_key = api.minio_api_key()
        address = api.address
        host = address.split(':')[0]
        os.system("mc config host add bk http://{}:{} {} {} --api s3v4".format(
                  host, api.data_port, username, minio_key['data']))

        click.echo('Login success')
        server_ver = api.version()
        click.echo("Server version: {}".format(server_ver))
    except MyelindlApiError as e:
        click.echo('Fail due to {}'.format(e))
        raise
