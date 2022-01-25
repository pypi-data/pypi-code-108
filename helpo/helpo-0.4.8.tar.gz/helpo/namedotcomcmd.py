import os

import typer
from loguru import logger

from helpo.namedotcom import Namecom

app = typer.Typer()


@logger.catch
@app.command()
def create_domain(domain_name: str,
                  nc_username: str = os.environ.get('NAMECOM_NAME'),
                  nc_token: str = os.environ.get('NAMECOM_TOKEN')):
    namecom_api = Namecom(nc_username, nc_token)
    domain_info = namecom_api.create_domain(domain_name)
    typer.echo(domain_info)


if __name__ == "__main__":
    app()
