"""CLI interface to Kfputils miscellaneous commands."""
import click
import logging
import sys
from kfp import Client
from .run_cli import run
from .pipeline_cli import pipeline


@click.group()
@click.option("--endpoint", help="Endpoint of the KFP API service to connect.")
@click.option("--iap-client-id", help="Client ID for IAP protected endpoint.")
@click.option(
    "-n",
    "--namespace",
    default="kubeflow",
    help="Kubernetes namespace to connect to the KFP API.",
)
@click.option(
    "--other-client-id",
    help="Client ID for IAP protected endpoint to obtain the refresh token.",
)
@click.option(
    "--other-client-secret",
    help="Client ID for IAP protected endpoint to obtain the refresh token.",
)
@click.pass_context
def cli(ctx, endpoint, iap_client_id, namespace, other_client_id, other_client_secret):
    """Kfputils is the missing CLI for Kubeflow pipelines."""
    namespace = "ns-ci"
    ctx.obj["client"] = Client(
        endpoint, iap_client_id, namespace, other_client_id, other_client_secret
    )
    ctx.obj["namespace"] = namespace


def main():
    """Init CLI."""
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    cli.add_command(run)
    cli.add_command(pipeline)
    try:
        # cli(obj={}, auto_envvar_prefix="KFPUTILS")
        cli(obj={})
    except Exception as e:
        logging.error(e)
        sys.exit(1)
