from __future__ import annotations

import argparse
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Collection, Optional

import pandas
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json
from annoworkcli.schedule.list_assigned_hours_daily import AssignedHoursDaily, ListAssignedHoursDaily
from annoworkcli.schedule.list_schedule import ListSchedule

logger = logging.getLogger(__name__)


class ListAssignedHoursDailyGroupbyTag:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str):
        self.annowork_service = annowork_service
        self.organization_id = organization_id
        self.list_schedule_obj = ListSchedule(annowork_service, organization_id)

    def get_assigned_hours_groupby_tag(
        self,
        assigned_hours_list: list[AssignedHoursDaily],
        target_organization_tag_ids: Optional[Collection[str]] = None,
        target_organization_tag_names: Optional[Collection[str]] = None,
    ) -> list[dict[str, Any]]:
        """アサイン時間のlistから、組織タグごとに集計したlistを返す。"""
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
                    "target_organization_tag_namesに含まれるいくつかのorganization_tag_nameは、存在しません。"
                    f":: {len(target_organization_tag_names)=}, {len(organization_tags)=}"
                )

        # dictのkeyはtuple[date, job_id, organization_tag_name]
        dict_hours: dict[tuple[str, str, str], float] = defaultdict(float)

        # 組織タグごと日毎の時間を集計する
        for organization_tag in organization_tags:
            organization_tag_name = organization_tag["organization_tag_name"]
            members = self.annowork_service.api.get_organization_tag_members(
                self.organization_id, organization_tag["organization_tag_id"]
            )
            member_ids = {e["organization_member_id"] for e in members}
            for elm in assigned_hours_list:
                if elm.organization_member_id in member_ids:
                    dict_hours[elm.date, elm.job_id, organization_tag_name] += elm.assigned_working_hours

        # 全体の時間を日毎に集計する

        # key:job_id, value:job_nameのdict
        job_dict: dict[str, str] = {}
        for elm in assigned_hours_list:
            dict_hours[elm.date, elm.job_id, "total"] += elm.assigned_working_hours
            job_dict[elm.job_id] = elm.job_name

        # dictのkeyは、tuple[date, job_id]
        dict_date: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
        for (date, job_id, org_tag), hours in dict_hours.items():
            dict_date[(date, job_id)].update({org_tag: hours})

        results = []
        for (date, job_id), value in dict_date.items():
            e = {"date": date, "job_id": job_id, "job_name": job_dict.get(job_id), "assigned_working_hours": value}
            results.append(e)

        results.sort(key=lambda e: (e["date"], e["job_id"]))
        return results

    def main(
        self,
        *,
        output: Path,
        output_format: OutputFormat,
        start_date: Optional[str],
        end_date: Optional[str],
        job_id_list: Optional[list[str]],
        user_id_list: Optional[list[str]],
        target_organization_tag_ids: Optional[Collection[str]],
        target_organization_tag_names: Optional[Collection[str]],
    ):
        list_obj = ListAssignedHoursDaily(self.annowork_service, self.organization_id)
        assigned_hours_list = list_obj.get_assigned_hours_daily_list(
            start_date=start_date,
            end_date=end_date,
            job_ids=job_id_list,
            user_ids=user_id_list,
        )
        if len(assigned_hours_list) == 0:
            logger.warning(f"アサイン時間情報は0件なので、出力しません。")
            return

        results = self.get_assigned_hours_groupby_tag(
            assigned_hours_list,
            target_organization_tag_ids=target_organization_tag_ids,
            target_organization_tag_names=target_organization_tag_names,
        )
        logger.info(f"{len(results)} 件のアサイン時間情報を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(results, is_pretty=True, output=output)
        else:
            df = pandas.json_normalize(results)
            df.fillna(0, inplace=True)
            required_columns = [
                "date",
                "job_id",
                "job_name",
                "assigned_working_hours.total",
            ]
            remaining_columns = list(set(df.columns) - set(required_columns))
            columns = required_columns + sorted(remaining_columns)

            print_csv(df[columns], output=output)


def main(args):
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    user_id_list = get_list_from_args(args.user_id)

    start_date: Optional[str] = args.start_date
    end_date: Optional[str] = args.end_date

    if all(v is None for v in [job_id_list, user_id_list, start_date, end_date]):
        logger.warning(
            "'--start_date'や'--job_id'などの絞り込み条件が1つも指定されていません。" "WebAPIから取得するデータ量が多すぎて、WebAPIのリクエストが失敗するかもしれません。"
        )

    organization_tag_id_list = get_list_from_args(args.organization_tag_id)
    organization_tag_name_list = get_list_from_args(args.organization_tag_name)

    ListAssignedHoursDailyGroupbyTag(annowork_service=annowork_service, organization_id=args.organization_id,).main(
        job_id_list=job_id_list,
        user_id_list=user_id_list,
        start_date=start_date,
        end_date=end_date,
        output=args.output,
        output_format=OutputFormat(args.format),
        target_organization_tag_ids=organization_tag_id_list,
        target_organization_tag_names=organization_tag_name_list,
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="絞り込み対象のユーザID")

    parser.add_argument("-j", "--job_id", type=str, nargs="+", required=False, help="取得対象のジョブID")

    parser.add_argument("--start_date", type=str, required=False, help="取得する範囲の開始日")
    parser.add_argument("--end_date", type=str, required=False, help="取得する範囲の終了日")

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
    subcommand_name = "list_daily_groupby_tag"
    subcommand_help = "日ごとのアサイン時間を、組織タグで集計した値を出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
