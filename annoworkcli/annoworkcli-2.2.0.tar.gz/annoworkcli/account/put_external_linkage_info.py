from __future__ import annotations

import argparse
import json
import logging
from typing import Any, Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, get_json_from_args

logger = logging.getLogger(__name__)


class PutExternalLinkageInfo:
    def __init__(self, annowork_service: AnnoworkResource):
        self.annowork_service = annowork_service

    def main(self, user_id: str, external_linkage_info: dict[str, Any]):
        old_info = self.annowork_service.wrapper.get_account_external_linkage_info_or_none(user_id)
        if old_info is None:
            logger.warning(f"user_id={user_id} のアカウント外部連携情報は存在しません。")
            return

        request_body = {
            "external_linkage_info": external_linkage_info,
            "last_updated_datetime": old_info["updated_datetime"],
        }

        self.annowork_service.api.put_account_external_linkage_info(user_id, request_body=request_body)
        logger.info(f"{user_id=} のユーザの外部連携情報を設定しました。")


def main(args):
    annowork_service = build_annoworkapi(args)
    external_linkage_info = get_json_from_args(args.external_linkage_info)
    PutExternalLinkageInfo(annowork_service=annowork_service).main(
        user_id=args.user_id, external_linkage_info=external_linkage_info
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-u",
        "--user_id",
        type=str,
        required=True,
        help="登録対象ユーザのuser_id",
    )

    SAMPLE_EXTERNAL_LINKAGE_INFO = {"annofab": {"account_id": "xxx"}}

    parser.add_argument(
        "--external_linkage_info",
        type=str,
        required=True,
        help="登録するアカウント外部連携情報。\n" f"(ex) ``{json.dumps(SAMPLE_EXTERNAL_LINKAGE_INFO)}`` ",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "put_external_linkage_info"
    subcommand_help = "アカウント外部連携情報取得を更新します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
