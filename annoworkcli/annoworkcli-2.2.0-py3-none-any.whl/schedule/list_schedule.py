from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Collection, Dict, Optional, Tuple

import pandas
from annoworkapi.enums import ScheduleType
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)

ExpectedWorkingHoursDict = Dict[Tuple[str, str], float]
"""keyがtuple(date, organization_member_id), valueが予定稼働時間のdict
"""


def create_assigned_hours_dict(
    schedule: dict[str, Any], expected_working_hours_dict: ExpectedWorkingHoursDict
) -> dict[str, float]:
    """作業計画情報からアサインされた時間の辞書（key:日付, value:アサイン時間）を返す。

    Args:
        schedule (dict[str,Any]): １つの作業計画情報
        expected_working_hours_dict (ExpectedWorkingHoursDict): 予定稼働時間情報のdict

    Returns:
        dict[str, float]: [description]
    """
    start_date = schedule["start_date"]
    end_date = schedule["end_date"]
    result = {}
    if schedule["type"] == ScheduleType.HOURS.value:
        for dt in pandas.date_range(start_date, end_date):
            date = str(dt.date())
            result[date] = schedule["value"]

    elif schedule["type"] == ScheduleType.PERCENTAGE.value:
        # 予定稼働時間の比率からアサインされた時間を算出する。
        for dt in pandas.date_range(schedule["start_date"], schedule["end_date"]):
            date = str(dt.date())
            expected_working_hours = expected_working_hours_dict.get((date, schedule["organization_member_id"]), 0)
            result[date] = expected_working_hours * schedule["value"] * 0.01

    return result


class ListSchedule:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

        self.organization_members = self.annowork_service.api.get_organization_members(
            self.organization_id, query_params={"includes_inactive_members": True}
        )

    def _set_assigned_hours(self, schedule_list: list[dict[str, Any]], min_date: str, max_date: str):
        query_params = {"term_start": min_date, "term_end": max_date}
        logger.debug(f"予定稼働時間を取得します。 :: {query_params=}")
        expected_working_times = self.annowork_service.api.get_expected_working_times(
            self.organization_id, query_params=query_params
        )
        expected_working_hours_dict = {
            (e["date"], e["organization_member_id"]): e["expected_working_hours"] for e in expected_working_times
        }
        for schedule in schedule_list:
            assigned_hours_dict = create_assigned_hours_dict(schedule, expected_working_hours_dict)
            schedule["assigned_working_hours"] = sum(assigned_hours_dict.values())

    def set_additional_info_to_schedule(self, schedule_list: list[dict[str, Any]]):
        """organization_member_id, job_idに紐づく情報, アサインされた時間を付与する。

        Args:
            schedule_list (list[dict[str,Any]]): (IN/OUT) 実績作業時間のリスト
        """
        if len(schedule_list) == 0:
            return

        organization_member_dict = {e["organization_member_id"]: e for e in self.organization_members}
        job_list = self.annowork_service.api.get_jobs(self.organization_id)
        job_dict = {e["job_id"]: e for e in job_list}

        # 予定稼働時間の取得範囲を決めるために、最小の日付と最大の日付も探す
        min_date = "9999-99-99"
        max_date = "0000-00-00"

        for schedule in schedule_list:
            min_date = min(min_date, schedule["start_date"])
            max_date = max(max_date, schedule["end_date"])

            organization_member_id = schedule["organization_member_id"]
            member = organization_member_dict.get(schedule["organization_member_id"])
            if member is None:
                logger.warning(
                    f"{organization_member_id=} である組織メンバは存在しません。 " f":: schedule_id= '{schedule['schedule_id']}' "
                )
                continue

            schedule["user_id"] = member["user_id"]
            schedule["username"] = member["username"]

            job_id = schedule["job_id"]
            job = job_dict.get(job_id)
            if job is None:
                logger.warning(f"{job_id=} であるジョブは存在しません。 " f":: schedule_id= '{schedule['schedule_id']}' ")
                continue
            schedule["job_name"] = job["job_name"]

        self._set_assigned_hours(schedule_list, min_date=min_date, max_date=max_date)

    def get_organization_member_id_list_from_user_id(self, user_id_list: Collection[str]) -> list[str]:
        organization_member_dict = {e["user_id"]: e["organization_member_id"] for e in self.organization_members}
        organization_member_id_list = []
        for user_id in user_id_list:
            organization_member_id = organization_member_dict.get(user_id)
            if organization_member_id is None:
                logger.warning(f"{user_id=} に該当する組織メンバが存在しませんでした。")
                continue
            organization_member_id_list.append(organization_member_id)
        return organization_member_id_list

    def get_schedules(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        job_ids: Optional[Collection[str]] = None,
        user_ids: Optional[Collection[str]] = None,
        is_set_additional_info: bool = False,
    ) -> list[dict[str, Any]]:
        """
        作業計画一覧を取得する。

        Args:
            start_date:
            end_date:
            job_id_list: 取得対象のジョブのjob_idのリスト
            user_id_list:
            is_set_additional_info: Trueなら名前などの付加情報を設定します。
        """

        query_params = {
            "term_start": start_date,
            "term_end": end_date,
        }

        schedule_list = []
        if job_ids is not None:
            for job_id in job_ids:
                query_params["job_id"] = job_id
                logger.debug(f"作業計画を取得します。 :: {query_params=}")
                schedule_list.extend(
                    self.annowork_service.api.get_schedules(self.organization_id, query_params=query_params)
                )
        else:
            logger.debug(f"作業計画を取得します。 :: {query_params=}")
            schedule_list.extend(
                self.annowork_service.api.get_schedules(self.organization_id, query_params=query_params)
            )

        if user_ids is not None:
            organization_member_id_list = self.get_organization_member_id_list_from_user_id(user_ids)
            schedule_list = [
                e for e in schedule_list if e["organization_member_id"] in set(organization_member_id_list)
            ]

        if is_set_additional_info is not None:
            self.set_additional_info_to_schedule(schedule_list)
        return schedule_list

    def main(
        self,
        *,
        output: Path,
        output_format: OutputFormat,
        start_date: Optional[str],
        end_date: Optional[str],
        job_id_list: Optional[list[str]],
        user_id_list: Optional[list[str]],
    ):
        result = self.get_schedules(
            start_date=start_date,
            end_date=end_date,
            job_ids=job_id_list,
            user_ids=user_id_list,
            is_set_additional_info=True,
        )
        if len(result) == 0:
            logger.warning(f"作業計画情報は0件なので、出力しません。")
            return

        logger.info(f"{len(result)} 件の作業計画情報を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(result, is_pretty=True, output=output)
        else:
            df = pandas.json_normalize(result)
            required_columns = [
                "organization_id",
                "schedule_id",
                "job_id",
                "job_name",
                "organization_member_id",
                "user_id",
                "username",
                "start_date",
                "end_date",
                "type",
                "value",
                "assigned_working_hours",
            ]
            remaining_columns = list(set(df.columns) - set(required_columns))
            columns = required_columns + remaining_columns

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

    ListSchedule(annowork_service=annowork_service, organization_id=args.organization_id,).main(
        job_id_list=job_id_list,
        user_id_list=user_id_list,
        start_date=start_date,
        end_date=end_date,
        output=args.output,
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

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="絞り込み対象のユーザID")

    parser.add_argument("-j", "--job_id", type=str, nargs="+", required=False, help="取得対象のジョブID")

    parser.add_argument("--start_date", type=str, required=False, help="取得する範囲の開始日")
    parser.add_argument("--end_date", type=str, required=False, help="取得する範囲の終了日")

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.add_argument(
        "-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list"
    subcommand_help = "作業計画の一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
