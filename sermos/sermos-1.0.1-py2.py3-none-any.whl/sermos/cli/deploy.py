""" Command Line Utilities for Sermos Deployments
"""
import logging
import click
from sermos.deploy import SermosDeploy

logger = logging.getLogger(__name__)


@click.group()
def deployment():
    """ Deployment command group.
    """


@deployment.command()
@click.option('--pkg-name', required=False, default=None)
@click.option('--sermos-yaml', required=False, default=None)
@click.option('--output-file', required=False, default=None)
def validate(pkg_name: str = None,
             sermos_yaml: str = None,
             output_file: str = None):
    """ Validate a compiled Sermos yaml is ready for deployment.

        Arguments::

            pkg-name (optional): Directory name for your Python package.
                e.g. my_package_name If none provided, will check environment
                for `SERMOS_CLIENT_PKG_NAME`. If not found, will exit.

            sermos-yaml (optional): Path to find your `sermos.yaml`
                configuration file. Defaults to `sermos.yaml`
    """
    # Instantiate SermosDeploy
    sd = SermosDeploy(access_key='fake',
                      pkg_name=pkg_name,
                      sermos_yaml_filename=sermos_yaml)

    # Validate deployment
    sd.validate_deployment(output_file=output_file)
    click.echo("Configuration is Valid and ready to Deploy.")


@deployment.command()
@click.option('--deployment-id', required=False, default=None)
@click.option('--access-key', required=False, default=None)
@click.option('--pkg-name', required=False, default=None)
@click.option('--sermos-yaml', required=False, default=None)
@click.option('--commit-hash', required=False, default=None)
@click.option('--base-url', required=False, default=None)
@click.option('--deploy-branch', required=False, default='main')
def deploy(deployment_id: str = None,
           access_key: str = None,
           pkg_name: str = None,
           sermos_yaml: str = None,
           commit_hash: str = None,
           base_url: str = None,
           deploy_branch: str = 'main'):
    """ Invoke a Sermos build for your application.

        Arguments:

            deployment-id (optional): UUID for Deployment. Find in your Sermos
                Cloud Console. Will look under `SERMOS_DEPLOYMENT_ID` in
                environment if not provided.

            access-key (optional): Defaults to checking the environment for
                `SERMOS_ACCESS_KEY`. If not found, will exit.

            pkg-name (optional): Directory name for your Python package.
                e.g. my_package_name If none provided, will check environment
                for `SERMOS_CLIENT_PKG_NAME`. If not found, will exit.

            sermos-yaml (optional): Path to find your `sermos.yaml`
                configuration file. Defaults to `sermos.yaml`

            commit-hash (optional): The specific commit hash of your git repo
                to deploy. If not provided, then current HEAD as of invocation
                will be used. This is the default usage, and is useful in the
                case of a CI/CD pipeline such that the Sermos deployment is
                invoked after your integration passes.

            base-url (optional): Defaults to primary Sermos Cloud base URL.
                    Only modify this if there is a specific, known reason to do so.

            deploy-branch (optional): Defaults to 'main'. Only modify this
                if there is a specific, known reason to do so.
    """
    # Instantiate SermosDeploy
    sd = SermosDeploy(deployment_id=deployment_id,
                      access_key=access_key,
                      pkg_name=pkg_name,
                      sermos_yaml_filename=sermos_yaml,
                      commit_hash=commit_hash,
                      base_url=base_url,
                      deploy_branch=deploy_branch)

    # Validate deployment
    sd.validate_deployment()

    # Invoke deployment
    result = sd.invoke_deployment()
    content = result.json()
    if result.status_code < 300:
        click.echo(content['data']['status'])
    else:
        logger.error(f"{content}")


@deployment.command()
@click.option('--deployment-id', required=False, default=None)
@click.option('--access-key', required=False, default=None)
@click.option('--base-url', required=False, default=None)
def status(deployment_id: str = None,
           access_key: str = None,
           base_url: str = None):
    """ Check on the status of a Sermos build.

        Arguments:
            deployment-id (optional): UUID for Deployment. Find in your Sermos
                Cloud Console. If not provided, looks in environment under
                `SERMOS_DEPLOYMENT_ID`
            access-key (optional): Defaults to checking the environment for
                `SERMOS_ACCESS_KEY`. If not found, will exit.
            base-url (optional): Defaults to primary Sermos Cloud base URL.
                    Only modify this if there is a specific, known reason to do so.
    """
    # Instantiate SermosDeploy
    sd = SermosDeploy(deployment_id=deployment_id,
                      access_key=access_key,
                      base_url=base_url)

    # Check deployment status
    result = sd.get_deployment_status()
    try:
        click.echo(result['data']['results'])
    except Exception as e:
        logger.error(f"{result} / {e}")
