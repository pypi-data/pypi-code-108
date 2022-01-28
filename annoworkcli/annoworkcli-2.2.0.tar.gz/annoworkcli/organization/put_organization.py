from __future__ import annotations

import argparse
import logging
from typing import Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi

logger = logging.getLogger(__name__)


class PutOrganization:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
    ):
        self.annowork_service = annowork_service

    def main(self, organization_id: str, organization_name: str, email: str):
        org = self.annowork_service.wrapper.get_organization_or_none(organization_id)

        request_body = {
            "organization_name": organization_name,
            "email": email,
        }
        if org is not None:
            request_body["last_updated_datetime"] = org["updated_datetime"]

        self.annowork_service.api.put_organization(organization_id, request_body=request_body)

        logger.info(f"組織 {organization_id} を作成/更新しました。")


def main(args):
    annowork_service = build_annoworkapi(args)

    PutOrganization(
        annowork_service=annowork_service,
    ).main(organization_id=args.organization_id, organization_name=args.organization_name, email=args.email)


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    parser.add_argument(
        "--organization_name",
        type=str,
        required=True,
        help="組織名",
    )

    parser.add_argument(
        "--email",
        type=str,
        required=True,
        help="組織管理者のe-mailアドレス",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "put"
    subcommand_help = "組織を登録/更新します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
