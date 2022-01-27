import click

from ethereum.logging_util import logging_basic_config
from ethereum.raw_data.job.verified_contract_extract_job import VerifiedContractExtractJob

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-s', '--start-block', default=0, show_default=True, type=int, help='Start block')
@click.option('-e', '--end-block', required=True, type=int, help='End block')
@click.option('-ss', '--step-size', default=10000, show_default=True, type=int)
@click.option('-wd', '--workspace-dir', default='/tmp/crypto-extract', show_default=True, type=str)
@click.option('-a', '--api-key', required=True, type=str)
@click.option('-c', '--cookie', required=True, type=str)
def extract_verified_contract(start_block: int,
                              end_block: int,
                              step_size: int,
                              workspace_dir: str,
                              api_key: str,
                              cookie: str):
    job = VerifiedContractExtractJob(
        resources=['verified_contract'],
        step_size=step_size,
        job_name='extract_verified_contracts',
        start_block=start_block,
        end_block=end_block,
        workspace_dir=workspace_dir,
        cookie=cookie,
        api_key=api_key
    )

    job.run()
