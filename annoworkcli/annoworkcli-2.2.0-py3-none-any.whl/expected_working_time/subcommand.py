import argparse
from typing import Optional

import annoworkcli
import annoworkcli.expected_working_time.delete_expected_working_time
import annoworkcli.expected_working_time.list_expected_working_time
import annoworkcli.expected_working_time.list_expected_working_time_groupby_tag


def parse_args(parser: argparse.ArgumentParser):

    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.expected_working_time.delete_expected_working_time.add_parser(subparsers)
    annoworkcli.expected_working_time.list_expected_working_time.add_parser(subparsers)
    annoworkcli.expected_working_time.list_expected_working_time_groupby_tag.add_parser(subparsers)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "expected_working_time"
    subcommand_help = "予定稼働時間関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False
    )
    parse_args(parser)
    return parser
