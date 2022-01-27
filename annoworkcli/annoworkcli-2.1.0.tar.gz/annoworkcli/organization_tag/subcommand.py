import argparse
from typing import Optional

import annoworkcli
import annoworkcli.organization_tag.list_organization_tag
import annoworkcli.organization_tag.put_organization_tag


def parse_args(parser: argparse.ArgumentParser):

    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.organization_tag.list_organization_tag.add_parser(subparsers)
    annoworkcli.organization_tag.put_organization_tag.add_parser(subparsers)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "organization_tag"
    subcommand_help = "組織タグ関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False
    )
    parse_args(parser)
    return parser
