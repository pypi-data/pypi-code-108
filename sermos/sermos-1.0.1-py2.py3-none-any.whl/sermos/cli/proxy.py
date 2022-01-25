""" Command Line Utilities for proxying into Sermos Cloud Services
"""
import logging
import click

from sermos.proxy import SermosProxy

logger = logging.getLogger(__name__)


@click.group()
def sermos_proxy():
    """ Deployment command group.
    """


@sermos_proxy.command()
@click.option('--proxy-id', required=True)
@click.option('--service-id', required=True)
@click.option('--local-port', required=True, default=8000)
@click.option('--local-host', required=False, default='127.0.0.1')
@click.option('--manual-select', required=False, is_flag=True)
@click.option('--deployment-id', required=False, default=None)
@click.option('--access-key', required=False, default=None)
@click.option('--base-url', required=False, default=None)
@click.option('--debug', required=False, is_flag=True)
def proxy(proxy_id: str,
          service_id: str,
          local_port: int = 8000,
          local_host: str = '127.0.0.1',
          manual_select: bool = False,
          deployment_id: str = None,
          access_key: str = None,
          base_url: str = None,
          debug: bool = False):
    """ Proxy a Sermos Cloud service and bind to local port.

    Connect to a Sermos Cloud service (typically a database) that is deployed
    behind Sermos' private network. This will allow for local development by
    proxying traffic to the cloud service and binding to a local port.

    Arguments::

        proxy-id: The proxy `nice id` for a service. This is found in
            your Sermos Cloud dashboard and is specific to each Deployment.

        service-id: The `nice id` for a service. This is found in
            your Sermos Cloud dashboard and is specific to each Deployment.

        deployment-id (optional): UUID for Deployment. Find in your Sermos
            Cloud Console. If not provided, looks in environment under
            `SERMOS_DEPLOYMENT_ID`

        local_port: Local port on which to bind.

        local_host: Local host ip on which to bind.

        manual_select: Manually choose the service/port selection from upstream
            service. Default behavior will use the standard DNS record and
            service port (recommended).

        access-key (optional): Defaults to checking the environment for
            `SERMOS_ACCESS_KEY`. If not found, will exit.

        base-url (optional): Defaults to primary Sermos Cloud base URL.
            Only modify this if there is a specific, known reason to do so.

        debug (optional): Rarely used. Local devleopment purposes only with
            variable/non-guaranteed behavior.
    """
    click.echo(f"Attempting to establish connection for `{service_id}` ...")
    try:
        auto_select = not manual_select
        sp = SermosProxy(proxy_id,
                         service_id,
                         local_port,
                         local_host,
                         deployment_id=deployment_id,
                         access_key=access_key,
                         base_url=base_url,
                         debug=debug)
        sp.connect(auto_select=auto_select)
    except ValueError as e:
        print(e)
