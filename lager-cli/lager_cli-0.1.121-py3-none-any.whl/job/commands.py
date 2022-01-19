"""
    lager.status.commands

    Status commands
"""
import math
import click
from ..status import run_job_output

@click.group(name='job')
def job():
    """
        Lager job commands
    """
    pass

@job.command()
@click.pass_context
@click.argument('job_id')
@click.option('--message-timeout', default=math.inf, type=click.FLOAT,
              help='Max time in seconds to wait between messages from API.'
              'This timeout only affects reading output and does not cancel the actual test run if hit.')
@click.option('--overall-timeout', default=math.inf, type=click.FLOAT,
              help='Cumulative time in seconds to wait for session output.'
              'This timeout only affects reading output and does not cancel the actual test run if hit.')
def status(ctx, job_id, message_timeout, overall_timeout):
    """
        Get job status
    """
    connection_params = ctx.obj.websocket_connection_params(socktype='job', job_id=job_id)
    run_job_output(connection_params, None, False, None, message_timeout, overall_timeout, 0, ctx.obj.debug)
