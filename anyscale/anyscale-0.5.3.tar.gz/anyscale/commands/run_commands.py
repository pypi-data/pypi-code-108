from typing import List

import click

from anyscale.authenticate import get_auth_api_client
from anyscale.background import run
from anyscale.sdk.anyscale_client.sdk import AnyscaleSDK
from anyscale.util import AnyscaleEndpointFormatter


@click.command(
    name="run",
    help="Run a shell command as a background job on anyscale. This command is currently experimental.",
    hidden=True,
)
@click.option(
    "--env",
    required=False,
    type=click.Path(exists=True),
    help="File to load the runtime environment from. Accepts YAML or JSON format",
)
@click.argument("commands", nargs=-1, type=str)
def anyscale_run(env: str, commands: List[str],) -> None:
    manager = run(" ".join(commands), runtime_env=env)
    completed = False
    try:
        manager.wait()
        completed = True
    finally:
        if not completed:
            endpoint_format = AnyscaleEndpointFormatter()
            print(
                f"""
    This job will continue to run in background mode on Anyscale.
    Job URL: {endpoint_format.get_job_endpoint(manager.id)}

    To kill this job, run the following in your terminal.

    `anyscale kill {manager.id}`
    """
            )


@click.command(
    name="kill",
    help="Kill a background job on anyscale. This command is currently experimental. "
    + "This command accepts the job id of a background job, and then kills it",
    hidden=True,
)
@click.argument("job_id", nargs=1, type=str)
def anyscale_kill_job(job_id: str) -> None:
    auth_api_client = get_auth_api_client()
    anyscale_sdk = AnyscaleSDK(auth_api_client.credentials, auth_api_client.host,)
    endpoint_format = AnyscaleEndpointFormatter()
    result = anyscale_sdk.kill_job(job_id).result
    print(
        f"""
Killed job with ID {result.id}.
Job URL: {endpoint_format.get_job_endpoint(job_id)}
"""
    )
