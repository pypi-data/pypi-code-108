from __future__ import annotations

import argparse
import datetime
import logging
from pathlib import Path
from typing import Any, Collection, Optional

import pandas
from annoworkapi.actual_working_time import get_term_start_end_from_date_for_actual_working_time
from annoworkapi.job import get_parent_job_id_from_job_tree
from annoworkapi.resource import Resource as AnnoworkResource
from annoworkapi.utils import str_to_datetime

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


class ListActualWorkingTime:
    def __init__(
        self, annowork_service: AnnoworkResource, organization_id: str, *, timezone_offset_hours: Optional[float]
    ):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

        self.organization_members = self.annowork_service.api.get_organization_members(
            self.organization_id, query_params={"includes_inactive_members": True}
        )

        # none 判定
        if timezone_offset_hours is not None:
            tzinfo = datetime.timezone(datetime.timedelta(hours=timezone_offset_hours))
        else:
            tzinfo = datetime.datetime.now().astimezone().tzinfo  # type: ignore
        self.tzinfo = tzinfo
        """日付に対するタイムゾーン"""

    def get_actual_working_times_by_organization_member(
        self,
        organization_member_id_list: list[str],
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:

        query_params = {}
        term_start, term_end = get_term_start_end_from_date_for_actual_working_time(
            start_date, end_date, tzinfo=self.tzinfo
        )
        if term_start is not None:
            query_params["term_start"] = term_start
        if term_end is not None:
            query_params["term_end"] = term_end

        result = []
        for organization_member_id in organization_member_id_list:
            logger.debug(f"実績時間情報を取得します。{organization_member_id=}, {query_params=}")
            tmp = self.annowork_service.api.get_actual_working_times_by_organization_member(
                self.organization_id, organization_member_id, query_params=query_params
            )
            result.extend(tmp)
        return result

    def get_actual_working_times_by_job(
        self,
        *,
        job_id_list: Optional[Collection[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        query_params = {}
        term_start, term_end = get_term_start_end_from_date_for_actual_working_time(
            start_date, end_date, tzinfo=self.tzinfo
        )
        if term_start is not None:
            query_params["term_start"] = term_start
        if term_end is not None:
            query_params["term_end"] = term_end

        if job_id_list is not None:
            result = []
            for job_id in job_id_list:
                query_params["job_id"] = job_id
                logger.debug(f"実績時間情報を取得します。{job_id=}, {query_params=}")
                tmp = self.annowork_service.api.get_actual_working_times(
                    self.organization_id, query_params=query_params
                )
                result.extend(tmp)
            return result
        else:
            logger.debug(f"実績時間情報を取得します。{query_params=}")
            return self.annowork_service.api.get_actual_working_times(self.organization_id, query_params=query_params)

    @staticmethod
    def get_actual_working_hours(actual_working_time: dict[str, Any]) -> float:
        delta = str_to_datetime(actual_working_time["end_datetime"]) - str_to_datetime(
            actual_working_time["start_datetime"]
        )
        return delta.total_seconds() / 3600

    def set_additional_info_to_actual_working_time(
        self, actual_working_time_list: list[dict[str, Any]], is_add_parent_job_info: bool = False
    ):
        """organization_member_id, job_idに紐づく情報を付与する。

        Args:
            actual_working_time_list (list[dict[str,Any]]): (IN/OUT) 実績作業時間のリスト
        """
        organization_member_dict = {e["organization_member_id"]: e for e in self.organization_members}
        job_list = self.annowork_service.api.get_jobs(self.organization_id)
        job_dict = {e["job_id"]: e for e in job_list}

        parent_job_id_set = {get_parent_job_id_from_job_tree(e["job_tree"]) for e in job_list}
        if None in parent_job_id_set:
            parent_job_id_set.remove(None)

        for actual in actual_working_time_list:
            organization_member_id = actual["organization_member_id"]
            member = organization_member_dict.get(actual["organization_member_id"])
            if member is None:
                logger.warning(
                    f"{organization_member_id=} である組織メンバは存在しません。 "
                    f":: actual_working_time_id= '{actual['actual_working_time_id']}' "
                )
                continue

            actual["actual_working_hours"] = self.get_actual_working_hours(actual)
            actual["user_id"] = member["user_id"]
            actual["username"] = member["username"]

            job_id = actual["job_id"]
            job = job_dict.get(job_id)
            if job is None:
                logger.warning(
                    f"{job_id=} であるジョブは存在しません。 " f":: actual_working_time_id= '{actual['actual_working_time_id']}' "
                )
                continue
            actual["job_name"] = job["job_name"]
            if is_add_parent_job_info:
                parent_job_id = get_parent_job_id_from_job_tree(job["job_tree"])
                actual["parent_job_id"] = parent_job_id
                if parent_job_id is not None:
                    parent_job = job_dict[parent_job_id]
                    actual["parent_job_name"] = parent_job["job_name"]
                else:
                    actual["parent_job_name"] = None

    def get_child_job_id_list(self, parent_job_id_list: Collection[str]) -> list[str]:
        results = []
        for parent_job_id in parent_job_id_list:
            job_list = self.annowork_service.api.get_job_children(self.organization_id, job_id=parent_job_id)
            results.extend([job["job_id"] for job in job_list])
        return results

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

    def get_actual_working_times(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        job_ids: Optional[Collection[str]] = None,
        parent_job_ids: Optional[Collection[str]] = None,
        user_ids: Optional[Collection[str]] = None,
        is_set_additional_info: bool = False,
        is_add_parent_job_info: bool = False,
    ) -> list[dict[str, Any]]:

        """実績業時間情報を取得する。

        以下の引数は排他的である。
        * job_id_list
        * parent_job_id_list

        Args:
            start_date:
            end_date:
            job_id_list: 取得対象のジョブのjob_idのリスト
            parent_job_id_list: 取得対象の親のジョブのjob_idのリスト
            user_id_list:
            is_set_additional_info: Trueなら名前などの付加情報を設定します。
        """
        organization_member_id_list: Optional[list[str]] = None
        if user_ids is not None:
            organization_member_id_list = self.get_organization_member_id_list_from_user_id(user_ids)

        if parent_job_ids is not None:
            # parent_job_id_list と job_id_listが両方not Noneになることはないので、job_id_listを上書きする
            job_ids = self.get_child_job_id_list(parent_job_ids)
            logger.debug(f"{parent_job_ids=} の子のジョブの {job_ids=}")

        # user_id_list, parent_job_id_list, job_id_listは排他なので、以下のような条件分岐にしている
        if organization_member_id_list is not None:
            result = self.get_actual_working_times_by_organization_member(
                organization_member_id_list=organization_member_id_list, start_date=start_date, end_date=end_date
            )
            # webapiではjob_idで絞り込めないので、クライアント側で絞り込む
            if job_ids is not None:
                result = [e for e in result if e["job_id"] in set(job_ids)]

        else:
            result = self.get_actual_working_times_by_job(job_id_list=job_ids, start_date=start_date, end_date=end_date)

        if is_set_additional_info is not None:
            self.set_additional_info_to_actual_working_time(result, is_add_parent_job_info=is_add_parent_job_info)
        return result

    def main(
        self,
        *,
        output: Path,
        output_format: OutputFormat,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        job_id_list: Optional[list[str]] = None,
        parent_job_id_list: Optional[list[str]] = None,
        user_id_list: Optional[list[str]] = None,
        is_add_parent_job_info: bool = False,
    ):
        result = self.get_actual_working_times(
            start_date=start_date,
            end_date=end_date,
            job_ids=job_id_list,
            parent_job_ids=parent_job_id_list,
            user_ids=user_id_list,
            is_set_additional_info=True,
            is_add_parent_job_info=is_add_parent_job_info,
        )
        if len(result) == 0:
            logger.warning(f"実績作業時間情報は0件なので、出力しません。")
            return

        logger.info(f"{len(result)} 件の実績作業時間情報を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(result, is_pretty=True, output=output)
        else:
            df = pandas.DataFrame(result)
            if is_add_parent_job_info:
                required_columns = [
                    "organization_id",
                    "actual_working_time_id",
                    "job_id",
                    "job_name",
                    "parent_job_id",
                    "parent_job_name",
                    "organization_member_id",
                    "user_id",
                    "username",
                    "start_datetime",
                    "end_datetime",
                    "actual_working_hours",
                    "note",
                ]
            else:
                required_columns = [
                    "organization_id",
                    "actual_working_time_id",
                    "job_id",
                    "job_name",
                    "organization_member_id",
                    "user_id",
                    "username",
                    "start_datetime",
                    "end_datetime",
                    "actual_working_hours",
                    "note",
                ]
            remaining_columns = list(set(df.columns) - set(required_columns))
            columns = required_columns + remaining_columns
            print_csv(df[columns], output=output)


def main(args):
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    user_id_list = get_list_from_args(args.user_id)
    start_date: Optional[str] = args.start_date
    end_date: Optional[str] = args.end_date

    if all(v is None for v in [job_id_list, parent_job_id_list, user_id_list, start_date, end_date]):
        logger.warning(
            "'--start_date'や'--job_id'などの絞り込み条件が1つも指定されていません。" "WebAPIから取得するデータ量が多すぎて、WebAPIのリクエストが失敗するかもしれません。"
        )

    ListActualWorkingTime(
        annowork_service=annowork_service,
        organization_id=args.organization_id,
        timezone_offset_hours=args.timezone_offset,
    ).main(
        job_id_list=job_id_list,
        parent_job_id_list=parent_job_id_list,
        user_id_list=user_id_list,
        start_date=start_date,
        end_date=end_date,
        is_add_parent_job_info=args.show_parent_job,
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

    # parent_job_idとjob_idの両方を指定するユースケースはなさそうなので、exclusiveにする。
    job_id_group = parser.add_mutually_exclusive_group()
    job_id_group.add_argument("-j", "--job_id", type=str, nargs="+", required=False, help="絞り込み対象のジョブID")
    job_id_group.add_argument("-pj", "--parent_job_id", type=str, nargs="+", required=False, help="絞り込み対象の親のジョブID")

    parser.add_argument("--start_date", type=str, required=False, help="取得する範囲の開始日（システムのローカルな日付）")
    parser.add_argument("--end_date", type=str, required=False, help="取得する範囲の終了日（システムのローカルな日付）")

    parser.add_argument(
        "--show_parent_job",
        action="store_true",
        help="親のジョブ情報も出力します。",
    )

    parser.add_argument(
        "--timezone_offset", type=float, help="日付に対するタイムゾーンのオフセット時間を指定します。例えばJSTなら '9' です。指定しない場合はローカルのタイムゾーンを参照します。"
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.add_argument(
        "-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list"
    subcommand_help = "実績作業時間情報の一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
