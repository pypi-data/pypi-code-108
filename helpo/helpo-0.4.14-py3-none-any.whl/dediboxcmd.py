import sys

import typer
from loguru import logger

from helpo.dedibox import Dedibox

app = typer.Typer()


@logger.catch
@app.command()
def is_server_available(server_id: str,
                        dedi_token: str = ''):
    dedi_api = Dedibox(dedi_token)
    server_info = dedi_api.is_server_available(server_id)
    if server_info['available']:
        typer.echo(server_info)
    else:
        typer.echo("No stock")
        sys.exit(1)


@logger.catch
@app.command()
def order_server(server_id: int, datacenter: int = 5,
                 support: str = 'basic', dedi_token: str = ''):
    dedi_api = Dedibox(dedi_token)
    server_info = dedi_api.order_server(server_id, datacenter, support)
    if server_info['id']:
        typer.echo(server_info)
    else:
        sys.exit(1)


if __name__ == "__main__":
    app()
