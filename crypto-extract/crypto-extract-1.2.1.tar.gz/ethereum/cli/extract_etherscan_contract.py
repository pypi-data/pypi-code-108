import click

from ethereum.logging_util import logging_basic_config
from ethereum.raw_data.job.etherscan_extract_job import EtherscanExtractJob

logging_basic_config()


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('-a', '--api-key', required=True, type=str)
@click.option('-c', '--cookie', required=True, type=str)
@click.option('-wd', '--workspace-dir', default='/tmp/crypto-extract', show_default=True, type=str)
def extract_etherscan_contract(api_key: str,
                               cookie: str,
                               workspace_dir: str):
    job = EtherscanExtractJob(
        workspace_dir=workspace_dir,
        api_key=api_key,
        cookie=cookie
    )

    job.run()
