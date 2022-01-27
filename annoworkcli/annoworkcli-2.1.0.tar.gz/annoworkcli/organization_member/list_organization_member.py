from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Collection, Optional

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class ListOrganization:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

    def set_additional_info(self, organization_members: list[dict[str, Any]]):
        logger.debug(f"{len(organization_members)} 件のメンバの組織タグ情報を取得します。")
        for member in organization_members:
            organization_tags = self.annowork_service.api.get_organization_member_tags(
                self.organization_id, member["organization_member_id"]
            )
            member["organization_tag_ids"] = [e["organization_tag_id"] for e in organization_tags]
            member["organization_tag_names"] = [e["organization_tag_name"] for e in organization_tags]

    def get_organization_members_from_tags(self, organization_tag_ids: Collection[str]) -> list[dict[str, Any]]:
        result = []
        for tag_id in organization_tag_ids:
            tmp = self.annowork_service.api.get_organization_tag_members(self.organization_id, tag_id)
            result.extend(tmp)

        # メンバが重複している可能性があるので取り除く
        # pandasのメソッドを使うために、一時的にDataFrameにする
        return pandas.DataFrame(result).drop_duplicates().to_dict("records")

    def main(
        self,
        output: Path,
        output_format: OutputFormat,
        organization_tag_ids: Optional[Collection[str]],
        show_organization_tag: bool,
    ):
        if organization_tag_ids is not None:
            organization_members = self.get_organization_members_from_tags(organization_tag_ids)
        else:
            organization_members = self.annowork_service.api.get_organization_members(
                self.organization_id, query_params={"includes_inactive_members": True}
            )

        if show_organization_tag:
            self.set_additional_info(organization_members)

        organization_members.sort(key=lambda e: e["user_id"].lower())

        if len(organization_members) == 0:
            logger.warning(f"組織メンバ情報は0件なので、出力しません。")
            return

        logger.debug(f"{len(organization_members)} 件の組織メンバ一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(organization_members, is_pretty=True, output=output)
        else:
            df = pandas.json_normalize(organization_members)
            print_csv(df, output=output)


def main(args):
    annowork_service = build_annoworkapi(args)
    organization_tag_id_list = get_list_from_args(args.organization_tag_id)
    ListOrganization(annowork_service=annowork_service, organization_id=args.organization_id).main(
        output=args.output,
        output_format=OutputFormat(args.format),
        organization_tag_ids=organization_tag_id_list,
        show_organization_tag=args.show_organization_tag,
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
        "-org_tag",
        "--organization_tag_id",
        nargs="+",
        type=str,
        help="指定した組織タグが付与された組織メンバを出力します。",
    )

    parser.add_argument(
        "--show_organization_tag",
        action="store_true",
        help="組織タグに関する情報も出力します。",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")
    parser.add_argument(
        "-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list"
    subcommand_help = "組織メンバの一覧を出力します。無効化されたメンバも出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
