""" Command Line Utilities for starting the local configuration server
"""
import logging
import click
from sermos.lib.config_server import api, set_api_config

logger = logging.getLogger(__name__)


@click.group()
def config_server():
    """ Deployment command group.
    """


@config_server.command()
@click.option('--base-dir', required=False, default=None)
@click.option('--pipelines-yaml', required=False, default=None)
@click.option('--schedules-json', required=False, default=None)
@click.option('--port', required=False, default=8000)
def local_config_api(base_dir: str = None,
                     pipelines_yaml: str = None,
                     schedules_json: str = None,
                     port: int = 8000):
    """ Start a local configuration API server for development.

    This will use the provided pipelines.yaml and schedules.json file to
    mock the API endpoints available to managed Sermos Deployments. To use
    for development, make sure to set the DEFAULT_BASE_URL in your application's
    environment (e.g. DEFAULT_BASE_URL=http://localhost:8000/api/v1/)

    Arguments::

        base-dir (optional): Directory name where your development config
            files reside. Defaults to `dev`.

        pipelines-yaml (optional): Path to find your `pipelines.yaml`
            configuration file. Defaults to `pipelines.yaml`

        schedules-json (optional): Path to find your `schedules.json`
            configuration file. Defaults to `schedules.json`
    """
    click.echo("Starting Local Sermos Configuration Server ...")
    set_api_config(base_dir=base_dir,
                   pipelines_yaml=pipelines_yaml,
                   schedules_json=schedules_json)

    api.run(port=port, host='0.0.0.0')
