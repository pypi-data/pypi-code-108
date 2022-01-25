import os

import typer
from loguru import logger

from helpo.remoteserver import RemoteServer

app = typer.Typer()


@logger.catch
@app.command()
def add_to_rundeck(username: str,
                   password: str,
                   ip: str,
                   port: int,
                   hostname: str,
                   ssh_key: str = None,
                   vault_url: str = 'https://vault.zadapps.info',
                   vault_token: str = os.environ.get('VAULT_TOKEN'),
                   vault_tenant: str = 'zadgroup',
                   minio_url: str = 'files.zadapps.info',
                   minio_access_key: str = None,
                   minio_secret_key: str = None):
    remote_server = RemoteServer(username, password, ip, port, ssh_key)
    remote_server.add_to_rundeck(hostname, vault_url, vault_token, vault_tenant, minio_url, minio_access_key,
                                 minio_secret_key)


if __name__ == "__main__":
    app()
