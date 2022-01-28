import argparse
import logging
from pathlib import Path
from typing import Optional

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class ListOrganizationTag:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

    def main(self, output: Path, output_format: OutputFormat):
        organization_tags = self.annowork_service.api.get_organization_tags(self.organization_id)

        if len(organization_tags) == 0:
            logger.warning(f"組織タグ情報は0件なので、出力しません。")
            return

        logger.debug(f"{len(organization_tags)} 件のタグ一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(organization_tags, is_pretty=True, output=output)
        else:
            df = pandas.json_normalize(organization_tags)
            required_columns = [
                "organization_id",
                "organization_tag_id",
                "organization_tag_name",
            ]
            remaining_columns = list(set(df.columns) - set(required_columns))
            columns = required_columns + remaining_columns
            print_csv(df[columns], output=output)


def main(args):
    annowork_service = build_annoworkapi(args)
    ListOrganizationTag(annowork_service=annowork_service, organization_id=args.organization_id).main(
        output=args.output, output_format=OutputFormat(args.format)
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.add_argument(
        "-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list"
    subcommand_help = "組織タグの一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
