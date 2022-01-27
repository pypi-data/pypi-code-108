from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Optional

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class ListOrganization:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
    ):
        self.annowork_service = annowork_service

    def get_organization_list(
        self,
        organization_id_list: Optional[list[str]] = None,
    ) -> list[dict[str, Any]]:
        if organization_id_list is None:
            return self.annowork_service.api.get_my_organizations()

        organization_list = []
        for organization_id in organization_id_list:
            org = self.annowork_service.wrapper.get_organization_or_none(organization_id)
            if org is None:
                logger.warning(f"{organization_id=} である組織は存在しませんでした。")
                continue
            organization_list.append(org)
        return organization_list

    def main(
        self,
        output: Path,
        output_format: OutputFormat,
        *,
        organization_id_list: Optional[list[str]],
    ):
        organization_list = self.get_organization_list(organization_id_list)
        if len(organization_list) == 0:
            logger.warning(f"組織情報は0件なので、出力しません。")
            return

        logger.debug(f"{len(organization_list)} 件の組織一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(organization_list, is_pretty=True, output=output)
        else:
            df = pandas.DataFrame(organization_list)
            print_csv(df, output=output)


def main(args):
    annowork_service = build_annoworkapi(args)
    organization_id_list = get_list_from_args(args.organization_id)
    ListOrganization(
        annowork_service=annowork_service,
    ).main(output=args.output, output_format=OutputFormat(args.format), organization_id_list=organization_id_list)


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        nargs="+",
        required=False,
        help="対象の組織IDを指定してください。未指定の場合は、自身の所属している組織一覧を出力します。",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.add_argument(
        "-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list"
    subcommand_help = "組織の一覧を取得します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
