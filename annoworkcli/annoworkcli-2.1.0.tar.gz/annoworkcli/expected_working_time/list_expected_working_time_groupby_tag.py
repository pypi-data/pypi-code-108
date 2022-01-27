from __future__ import annotations

import argparse
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Collection, Optional

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import COMMAND_LINE_ERROR_STATUS_CODE, OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.expected_working_time.list_expected_working_time import ListExpectedWorkingTime

logger = logging.getLogger(__name__)


class ListExpectedWorkingTimeGroupbyTag:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

    def get_expected_working_times_groupby_tag(
        self,
        expected_working_times: list[dict[str, Any]],
        target_organization_tag_ids: Optional[Collection[str]] = None,
        target_organization_tag_names: Optional[Collection[str]] = None,
    ) -> list[dict[str, Any]]:
        """予定稼働時間のlistから、組織タグごとに集計したlistを返す。

        Args:
            expected_working_times (list[dict[str,Any]]): [description]

        Returns:
            list[dict[str,Any]]: [description]
        """
        organization_tags = self.annowork_service.api.get_organization_tags(self.organization_id)

        # target_organization_tag_idsとtarget_organization_tag_namesは排他的なので、両方not Noneになることはない
        assert not (target_organization_tag_ids is not None and target_organization_tag_names is not None)
        if target_organization_tag_ids is not None:
            organization_tags = [
                e for e in organization_tags if e["organization_tag_id"] in set(target_organization_tag_ids)
            ]
            if len(organization_tags) != len(target_organization_tag_ids):
                logger.warning(
                    f"target_organization_tag_idsに含まれるいくつかのorganization_tag_idは、存在しません。"
                    f":: {len(target_organization_tag_ids)=}, {len(organization_tags)=}"
                )

        if target_organization_tag_names is not None:
            organization_tags = [
                e for e in organization_tags if e["organization_tag_name"] in set(target_organization_tag_names)
            ]
            if len(organization_tags) != len(target_organization_tag_names):
                logger.warning(
                    f"target_organization_tag_namesに含まれるいくつかのorganization_tag_nameは、存在しません。"
                    f":: {len(target_organization_tag_names)=}, {len(organization_tags)=}"
                )

        dict_hours: dict[tuple[str, str], float] = defaultdict(float)

        # 組織タグごと日毎の時間を集計する
        for organization_tag in organization_tags:
            organization_tag_name = organization_tag["organization_tag_name"]
            members = self.annowork_service.api.get_organization_tag_members(
                self.organization_id, organization_tag["organization_tag_id"]
            )
            member_ids = {e["organization_member_id"] for e in members}
            for elm in expected_working_times:
                if elm["organization_member_id"] in member_ids:
                    dict_hours[elm["date"], organization_tag_name] += elm["expected_working_hours"]

        # 全体の時間を日毎に集計する
        for elm in expected_working_times:
            dict_hours[elm["date"], "total"] += elm["expected_working_hours"]

        dict_date: dict[str, dict[str, float]] = defaultdict(dict)
        for (date, org_tag), hours in dict_hours.items():
            dict_date[date].update({org_tag: hours})

        results = []

        for date, value in dict_date.items():
            elm = {"date": date, "expected_working_hours": value}
            results.append(elm)

        results.sort(key=lambda e: (e["date"]))
        return results

    def main(
        self,
        *,
        output: Path,
        output_format: OutputFormat,
        user_id_list: Optional[list[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        target_organization_tag_ids: Optional[Collection[str]] = None,
        target_organization_tag_names: Optional[Collection[str]] = None,
    ):
        list_obj = ListExpectedWorkingTime(self.annowork_service, self.organization_id)
        if user_id_list is not None:
            expected_working_times = list_obj.get_expected_working_times_by_user_id(
                user_id_list=user_id_list, start_date=start_date, end_date=end_date
            )
        else:
            expected_working_times = list_obj.get_expected_working_times(start_date=start_date, end_date=end_date)

        if len(expected_working_times) == 0:
            logger.warning(f"予定稼働時間情報0件なので、出力しません。")
            return

        results = self.get_expected_working_times_groupby_tag(
            expected_working_times,
            target_organization_tag_ids=target_organization_tag_ids,
            target_organization_tag_names=target_organization_tag_names,
        )

        logger.info(f"{len(results)} 件の組織タグで集計した予定稼働時間の一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(results, is_pretty=True, output=output)
        else:
            df = pandas.json_normalize(results)
            df.fillna(0, inplace=True)
            required_columns = [
                "date",
                "expected_working_hours.total",
            ]
            remaining_columns = list(set(df.columns) - set(required_columns))
            columns = required_columns + sorted(remaining_columns)

            print_csv(df[columns], output=output)


def main(args):
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    start_date: Optional[str] = args.start_date
    end_date: Optional[str] = args.end_date

    command = " ".join(sys.argv[0:3])
    if all(v is None for v in [user_id_list, start_date, end_date]):
        print(f"{command}: error: '--start_date'や'--user_id'などの絞り込み条件を1つ以上指定してください。", file=sys.stderr)
        sys.exit(COMMAND_LINE_ERROR_STATUS_CODE)

    organization_tag_id_list = get_list_from_args(args.organization_tag_id)
    organization_tag_name_list = get_list_from_args(args.organization_tag_name)

    ListExpectedWorkingTimeGroupbyTag(annowork_service=annowork_service, organization_id=args.organization_id).main(
        user_id_list=user_id_list,
        start_date=args.start_date,
        end_date=args.end_date,
        output=args.output,
        target_organization_tag_ids=organization_tag_id_list,
        target_organization_tag_names=organization_tag_name_list,
        output_format=OutputFormat(args.format),
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="集計対象のユーザID")

    parser.add_argument("--start_date", type=str, required=False, help="集計開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=False, help="集計終了日(YYYY-mm-dd)")

    org_tag_group = parser.add_mutually_exclusive_group()
    org_tag_group.add_argument(
        "-org_tag",
        "--organization_tag_id",
        type=str,
        nargs="+",
        help="出力対象の組織タグID。未指定の場合は全ての組織タグを出力します。",
    )

    org_tag_group.add_argument(
        "--organization_tag_name",
        type=str,
        nargs="+",
        help="出力対象の組織タグ名。未指定の場合は全ての組織タグを出力します。",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")
    parser.add_argument(
        "-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list_groupby_tag"
    subcommand_help = "組織タグで集計した予定稼働時間の一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
