from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi
from annoworkcli.common.utils import print_json

logger = logging.getLogger(__name__)


class GetMyAccount:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
    ):
        self.annowork_service = annowork_service

    def main(self, output: Optional[Path]):
        my_account = self.annowork_service.api.get_my_account()
        print_json(my_account, output=output, is_pretty=True)


def main(args):
    annowork_service = build_annoworkapi(args)

    GetMyAccount(
        annowork_service=annowork_service,
    ).main(output=args.output)


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument("-o", "--output", type=Path, required=False, help="出力先")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "get"
    subcommand_help = "ログイン中のアカウント情報を出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )

    parse_args(parser)
    return parser
