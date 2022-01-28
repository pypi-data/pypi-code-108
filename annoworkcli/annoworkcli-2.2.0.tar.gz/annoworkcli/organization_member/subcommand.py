import argparse
from typing import Optional

import annoworkcli
import annoworkcli.organization_member.append_tag_to_organization_member
import annoworkcli.organization_member.change_organization_member_properties
import annoworkcli.organization_member.delete_organization_member
import annoworkcli.organization_member.list_organization_member
import annoworkcli.organization_member.put_organization_member
import annoworkcli.organization_member.remove_tag_to_organization_member


def parse_args(parser: argparse.ArgumentParser):

    subparsers = parser.add_subparsers(dest="subcommand_name")

    # サブコマンドの定義
    annoworkcli.organization_member.append_tag_to_organization_member.add_parser(subparsers)
    annoworkcli.organization_member.change_organization_member_properties.add_parser(subparsers)
    annoworkcli.organization_member.delete_organization_member.add_parser(subparsers)
    annoworkcli.organization_member.list_organization_member.add_parser(subparsers)

    annoworkcli.organization_member.put_organization_member.add_parser(subparsers)
    annoworkcli.organization_member.remove_tag_to_organization_member.add_parser(subparsers)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "organization_member"
    subcommand_help = "組織メンバ関係のサブコマンド"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help, is_subcommand=False
    )
    parse_args(parser)
    return parser
