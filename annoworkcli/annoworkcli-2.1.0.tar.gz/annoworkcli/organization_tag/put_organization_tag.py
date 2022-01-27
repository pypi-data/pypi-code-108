from __future__ import annotations

import argparse
import logging
import uuid
from typing import Optional

from annoworkapi.resource import Resource as AnnoworkResource
from more_itertools import first_true

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi

logger = logging.getLogger(__name__)


class PutOrganizationTag:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

    def main(self, organization_tag_name: str, organization_tag_id: Optional[str]):
        organization_tags = self.annowork_service.api.get_organization_tags(self.organization_id)

        if organization_tag_id is None:
            organization_tag_id = str(uuid.uuid4())

        old_organization_tag = first_true(
            organization_tags, pred=lambda e: e["organization_tag_id"] == organization_tag_id
        )
        request_body = {"organization_tag_name": organization_tag_name}
        if old_organization_tag is not None:
            request_body["last_updated_datetime"] = old_organization_tag["updated_datetime"]

        content = self.annowork_service.api.put_organization_tag(
            self.organization_id, organization_tag_id, request_body=request_body
        )
        logger.debug(f"{organization_tag_name=} を登録しました。{content=}")


def main(args):
    annowork_service = build_annoworkapi(args)
    PutOrganizationTag(annowork_service=annowork_service, organization_id=args.organization_id).main(
        organization_tag_name=args.organization_tag_name, organization_tag_id=args.organization_tag_id
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    parser.add_argument(
        "--organization_tag_name",
        type=str,
        required=True,
        help="登録対象の組織タグの名前",
    )

    parser.add_argument(
        "-org_tag",
        "--organization_tag_id",
        type=str,
        required=True,
        help="登録対象の組織タグのID",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "put"
    subcommand_help = "組織タグを更新します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
