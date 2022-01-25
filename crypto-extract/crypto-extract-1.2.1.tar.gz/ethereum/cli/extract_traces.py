import click

from ethereum.logging_util import logging_basic_config
from ethereum.raw_data.job.trace_extract_job import TraceExtractJob

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start-block', default=0, show_default=True, type=int, help='Start block')
@click.option('-e', '--end-block', required=True, type=int, help='End block')
@click.option('-b', '--batch-size', default=100, show_default=True, type=int,
              help='The number of blocks to export at a time.')
@click.option('-p', '--provider-uri', default='https://mainnet.infura.io', show_default=True, type=str,
              help='The URI of the web3 provider e.g. '
                   'file://$HOME/Library/Ethereum/geth.ipc or https://mainnet.infura.io')
@click.option('-w', '--max-workers', default=5, show_default=True, type=int, help='The maximum number of workers.')
@click.option('-ss', '--step-size', default=10000, show_default=True, type=int)
@click.option('-wd', '--workspace-dir', default='/tmp/crypto-extract', show_default=True, type=str)
def extract_traces(start_block: int,
                   end_block: int,
                   batch_size: int,
                   provider_uri: str,
                   max_workers: int,
                   step_size: int,
                   workspace_dir: str):
    job = TraceExtractJob(
        resources=['trace'],
        step_size=step_size,
        job_name='trace',
        start_block=start_block,
        end_block=end_block,
        workspace_dir=workspace_dir,
        uri=provider_uri,
        batch_size=batch_size,
        max_workers=max_workers
    )

    job.run()
