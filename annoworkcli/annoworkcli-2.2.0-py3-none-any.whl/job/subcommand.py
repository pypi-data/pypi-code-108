import argparse
from typing import Optional

import annoworkcli
import annoworkcli.job.change_job_properties
import annoworkcli.job.delete_job
import annoworkcli.job.list_job


def parse_args(parser: argparse.ArgumentParser):

    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.job.change_job_properties.add_parser(subparsers)
    annoworkcli.job.delete_job.add_parser(subparsers)
    annoworkcli.job.list_job.add_parser(subparsers)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "job"
    subcommand_help = "ジョブ関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False
    )
    parse_args(parser)
    return parser
