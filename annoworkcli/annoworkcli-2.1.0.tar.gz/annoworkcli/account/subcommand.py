import argparse
from typing import Optional

import annoworkcli
import annoworkcli.account.list_external_linkage_info
import annoworkcli.account.put_external_linkage_info


def parse_args(parser: argparse.ArgumentParser):

    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.account.list_external_linkage_info.add_parser(subparsers)
    annoworkcli.account.put_external_linkage_info.add_parser(subparsers)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "account"
    subcommand_help = "ユーザアカウントに関するサブコマンド"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False
    )
    parse_args(parser)
    return parser
