from __future__ import annotations

import argparse
import datetime
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas
from annoworkapi.resource import Resource as AnnoworkResource
from dataclasses_json import DataClassJsonMixin

import annoworkcli
from annoworkcli.actual_working_time.list_actual_working_hours_daily import create_actual_working_hours_daily_list
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime
from annoworkcli.common.annofab import TIMEZONE_OFFSET_HOURS, get_annofab_project_id_from_job
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)

ActualWorkingHoursDict = Dict[Tuple[datetime.date, str, str], float]
"""実績作業時間の日ごとの情報を格納する辞書
key: (date, organization_member_id, job_id), value: 実績作業時間
"""


@dataclass
class AnnofabLabor(DataClassJsonMixin):
    """Annofab用の実績作業時間情報"""

    date: str
    account_id: str
    project_id: str
    actual_worktime_hour: float


JobIdAnnofabProjectIdDict = Dict[str, str]
"""key:job_id, value:annofab_project_idのdict
"""


class ListLabor:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

        self.all_job_list = self.annowork_service.api.get_jobs(self.organization_id)

        # Annofabが日本時間に固定されているので、それに合わせて timezone_offset_hours を指定する。
        self.list_actual_working_time_obj = ListActualWorkingTime(
            annowork_service=annowork_service,
            organization_id=organization_id,
            timezone_offset_hours=TIMEZONE_OFFSET_HOURS,
        )

    def get_job_id_annofab_project_id_dict_from_annofab_project_id(
        self, annofab_project_id_list: list[str]
    ) -> JobIdAnnofabProjectIdDict:
        annofab_project_id_dict = {
            get_annofab_project_id_from_job(job): job["job_id"]
            for job in self.all_job_list
            if get_annofab_project_id_from_job(job) is not None
        }

        result = {}
        for annofab_project_id in annofab_project_id_list:
            job_id = annofab_project_id_dict.get(annofab_project_id)
            if job_id is None:
                logger.warning(f"ジョブの外部連携情報に、AnnoFabのプロジェクトID '{annofab_project_id}' を表すURLが設定されたジョブは見つかりませんでした。")
                continue

            result[job_id] = annofab_project_id

        return result

    def get_job_id_annofab_project_id_dict_from_job_id(self, job_id_list: list[str]) -> JobIdAnnofabProjectIdDict:
        job_id_dict = {
            job["job_id"]: get_annofab_project_id_from_job(job)
            for job in self.all_job_list
            if get_annofab_project_id_from_job(job) is not None
        }

        result = {}
        for job_id in job_id_list:
            annofab_project_id = job_id_dict.get(job_id)
            if annofab_project_id is None:
                logger.warning(f"{job_id=} のジョブの外部連携情報にAnnoFabのプロジェクトを表すURLは設定されていませんでした。")
                continue

            result[job_id] = annofab_project_id

        return result

    def get_user_id_annofab_account_id_dict(self, user_id_set) -> dict[str, str]:
        result = {}
        for user_id in user_id_set:
            annofab_account_id = self.annowork_service.wrapper.get_annofab_account_id_from_user_id(user_id)
            if annofab_account_id is None:
                logger.warning(f"{user_id=} の外部連携情報にAnnofabのaccount_idが設定されていません。")
                continue
            result[user_id] = annofab_account_id
        return result

    def get_annofab_labor_list(
        self,
        job_id_list: Optional[list[str]],
        annofab_project_id_list: Optional[list[str]],
        start_date: Optional[str],
        end_date: Optional[str],
    ) -> list[AnnofabLabor]:
        # job_id_listとjob_id_annofab_project_id_dictのどちらかは必ずnot None
        assert job_id_list is not None or annofab_project_id_list is not None
        if job_id_list is not None:
            job_id_annofab_project_id_dict = self.get_job_id_annofab_project_id_dict_from_job_id(job_id_list)

            actual_working_time_list = self.list_actual_working_time_obj.get_actual_working_times(
                job_ids=job_id_list, start_date=start_date, end_date=end_date, is_set_additional_info=True
            )

        elif annofab_project_id_list is not None:
            job_id_annofab_project_id_dict = self.get_job_id_annofab_project_id_dict_from_annofab_project_id(
                annofab_project_id_list
            )
            actual_working_time_list = self.list_actual_working_time_obj.get_actual_working_times(
                job_ids=job_id_annofab_project_id_dict.keys(),
                start_date=start_date,
                end_date=end_date,
                is_set_additional_info=True,
            )

        if len(actual_working_time_list) == 0:
            return []

        # annofabのデータは日本時間に固定されているので、日本時間を指定する
        daily_list = create_actual_working_hours_daily_list(
            actual_working_time_list, timezone_offset_hours=TIMEZONE_OFFSET_HOURS
        )

        user_id_set = {elm.user_id for elm in daily_list}
        user_id_annofab_account_id_dict = self.get_user_id_annofab_account_id_dict(user_id_set)
        if len(user_id_set) != len(user_id_annofab_account_id_dict):
            raise RuntimeError(f"アカウント外部連携情報にAnnofabのaccount_idが設定されていないユーザがいます。")

        result = []
        for elm in daily_list:
            annofab_project_id = job_id_annofab_project_id_dict[elm.job_id]
            annofab_account_id = user_id_annofab_account_id_dict[elm.user_id]
            result.append(
                AnnofabLabor(
                    date=elm.date,
                    account_id=annofab_account_id,
                    project_id=annofab_project_id,
                    actual_worktime_hour=elm.actual_working_hours,
                )
            )
        return result


def main(args):
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    annofab_project_id_list = get_list_from_args(args.annofab_project_id)
    start_date: Optional[str] = args.start_date
    end_date: Optional[str] = args.end_date

    annofab_labor_list = ListLabor(annowork_service, args.organization_id).get_annofab_labor_list(
        job_id_list=job_id_list,
        annofab_project_id_list=annofab_project_id_list,
        start_date=start_date,
        end_date=end_date,
    )

    if len(annofab_labor_list) == 0:
        logger.warning(f"日ごとの実績作業時間情報は0件なので、出力しません。")
        return

    logger.info(f"{len(annofab_labor_list)} 件の日ごとの実績作業時間情報を出力します。")

    if OutputFormat(args.format) == OutputFormat.JSON:
        # `.schema().dump(many=True)`を使わない理由：使うと警告が発生するから
        # https://qiita.com/yuji38kwmt/items/a3625b2011aff1d9901b
        dict_result = []
        for elm in annofab_labor_list:
            dict_result.append(elm.to_dict())
        print_json(dict_result, is_pretty=True, output=args.output)
    else:
        df = pandas.DataFrame(annofab_labor_list)
        print_csv(df, output=args.output)


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    job_id_group = parser.add_mutually_exclusive_group(required=True)
    job_id_group.add_argument("-j", "--job_id", type=str, nargs="+", help="絞り込み対象のジョブID")
    job_id_group.add_argument("-af_p", "--annofab_project_id", type=str, nargs="+", help="絞り込み対象のAnnoFabのプロジェクトID")

    parser.add_argument("--start_date", type=str, required=False, help="集計開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=False, help="集計終了日(YYYY-mm-dd)")

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.add_argument(
        "-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list_labor"
    subcommand_help = "AnnoFabのフォーマットに従った実績作業時間の一覧を出力します。"
    description = (
        "AnnoFabのフォーマットに従った実績作業時間の一覧を出力します。\n"
        "出力したCSVファイルは、 'annofabcli statistics visualize' コマンドの '--labor_csv' に渡せます。"
    )

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=description)
    parse_args(parser)
    return parser
