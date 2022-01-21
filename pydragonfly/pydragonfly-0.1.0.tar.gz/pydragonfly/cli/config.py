import click
import click_creds
from rich import print as rprint
from typing import Optional

from ._utils import ClickContext


@click.group("config")
def config():
    """
    Set or view config variables
    """


@config.command("get")
@click_creds.pass_netrcstore_obj
def config_get(netrc: click_creds.NetrcStore):
    """
    Pretty Print config variables
    """
    rprint(netrc.host_with_mapping)


@config.command("set")
@click.option(
    "-k",
    "--api-key",
    help="Dragonfly API key",
)
@click.option(
    "-c",
    "--certificate",
    type=click.Path(exists=True, resolve_path=True),
    help="Path to SSL client certificate file (.pem)",
)
@click.option(
    "-u",
    "--instance-url",
    default="https://dragonfly.certego.net",
    show_default=True,
    help="Dragonfly's server URL",
)
@click.option(
    "-v",
    "--verify",
    is_flag=True,
    show_default=True,
    help="Boolean determining whether certificate validation is enforced",
)
@click.pass_context
def config_set(
    ctx: ClickContext,
    api_key: Optional[str],
    certificate: Optional[str],
    instance_url: str,
    verify: bool,
):
    """
    Set/Edit config variables
    """
    netrc: click_creds.NetrcStore = click_creds.get_netrc_object_from_ctx(ctx)
    new_host = netrc.host.copy()
    if api_key:
        new_host["password"] = api_key
    if instance_url:
        new_host["account"] = instance_url
    if certificate:
        new_host["login"] = certificate
    if verify is False:
        new_host["login"] = False
    # finally save
    netrc.save(new_host)
    ctx.obj._logger.info("Successfully saved config variables!")
