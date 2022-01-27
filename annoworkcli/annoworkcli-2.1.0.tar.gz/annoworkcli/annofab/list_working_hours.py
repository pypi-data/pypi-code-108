from __future__ import annotations

import argparse
import functools
import itertools
import logging
import multiprocessing
import sys
from pathlib import Path
from typing import Any, Collection, Optional

import pandas
import requests
from annofabapi import build as build_annofabapi
from annofabapi.resource import Resource as AnnofabResource
from annoworkapi.job import get_parent_job_id_from_job_tree
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.actual_working_time.list_actual_working_hours_daily import (
    ActualWorkingHoursDaily,
    create_actual_working_hours_daily_list,
    filter_actual_daily_list,
)
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime
from annoworkcli.common.annofab import TIMEZONE_OFFSET_HOURS, get_annofab_project_id_from_job, isoduration_to_hour
from annoworkcli.common.cli import COMMAND_LINE_ERROR_STATUS_CODE, OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


def _get_get_df_working_hours_from_df(
    *,
    df_actual_working_hours: pandas.DataFrame,
    df_user_and_af_account: pandas.DataFrame,
    df_job_and_af_project: pandas.DataFrame,
    df_af_working_hours: pandas.DataFrame,
) -> pandas.DataFrame:

    # annowork側の作業時間情報
    df_aw_working_hours = df_actual_working_hours.merge(
        df_user_and_af_account[["user_id", "annofab_account_id"]], how="left", on="user_id"
    ).merge(
        df_job_and_af_project[["job_id", "annofab_project_id"]],
        how="left",
        on="job_id",
    )

    if len(df_af_working_hours) == 0:
        logger.warning(f"AnnoFabの作業時間情報が0件でした。")
        df_aw_working_hours["annofab_working_hours"] = 0
        return df_aw_working_hours

    df_merged = df_aw_working_hours.merge(
        df_af_working_hours, how="outer", on=["date", "annofab_project_id", "annofab_account_id"]
    )

    TMP_SUFFIX = "_tmp"
    # df_merged は outer joinしているため、左側にも欠損値ができる。
    # それを埋めるために、以前に user情報, job情報の一意なdataframeを生成して、欠損値を埋める
    USER_COLUMNS = ["organization_member_id", "user_id", "username"]
    df_merged = df_merged.merge(
        df_user_and_af_account, how="left", on="annofab_account_id", suffixes=(None, TMP_SUFFIX)
    )
    for user_column in USER_COLUMNS:
        df_merged[user_column].fillna(df_merged[f"{user_column}{TMP_SUFFIX}"], inplace=True)

    JOB_COLUMNS = ["job_id", "job_name"]
    df_merged = df_merged.merge(df_job_and_af_project, how="left", on="annofab_project_id", suffixes=(None, TMP_SUFFIX))
    for job_column in JOB_COLUMNS:
        df_merged[job_column].fillna(df_merged[f"{job_column}{TMP_SUFFIX}"], inplace=True)

    df_merged.fillna(
        {
            "actual_working_hours": 0,
            "annofab_working_hours": 0,
        },
        inplace=True,
    )

    return df_merged[
        ["date"]
        + JOB_COLUMNS
        + USER_COLUMNS
        + ["actual_working_hours", "annofab_project_id", "annofab_account_id", "annofab_working_hours", "notes"]
    ]


class ListWorkingHoursWithAnnofab:
    def __init__(
        self,
        *,
        annowork_service: AnnoworkResource,
        organization_id: str,
        annofab_service: AnnofabResource,
        parallelism: Optional[int] = None,
    ):
        self.annowork_service = annowork_service
        self.organization_id = organization_id
        self.annofab_service = annofab_service
        self.parallelism = parallelism

        self.all_jobs = self.annowork_service.api.get_jobs(self.organization_id)
        self.all_organization_members = self.annowork_service.api.get_organization_members(
            self.organization_id, query_params={"includes_inactive_members": True}
        )

        self.list_actual_working_time_obj = ListActualWorkingTime(
            annowork_service, organization_id, timezone_offset_hours=TIMEZONE_OFFSET_HOURS
        )

    def get_actual_working_hours_daily(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        job_ids: Optional[Collection[str]] = None,
        parent_job_ids: Optional[Collection[str]] = None,
        user_ids: Optional[Collection[str]] = None,
    ) -> list[ActualWorkingHoursDaily]:
        actual_working_time_list = self.list_actual_working_time_obj.get_actual_working_times(
            job_ids=job_ids,
            parent_job_ids=parent_job_ids,
            user_ids=user_ids,
            start_date=start_date,
            end_date=end_date,
            is_set_additional_info=False,
        )
        self.list_actual_working_time_obj.set_additional_info_to_actual_working_time(actual_working_time_list)

        result = create_actual_working_hours_daily_list(
            actual_working_time_list, timezone_offset_hours=TIMEZONE_OFFSET_HOURS
        )
        result = filter_actual_daily_list(result, start_date=start_date, end_date=end_date)
        return result

    def _get_df_user_and_af_account(self, user_ids: Collection[str]) -> pandas.DataFrame:
        """ユーザ情報とAnnofabのアカウント情報格納されたpandas.DataFrameを返します。
        以下の列を持ちます。
        * user_id
        * username
        * organization_member_id
        * annofab_account_id
        """
        af_account_list = []
        logger.debug(f"{len(user_ids)} 件のユーザのアカウント外部連携情報を取得します。")
        for user_id in user_ids:
            annofab_account_id = self.annowork_service.wrapper.get_annofab_account_id_from_user_id(user_id)
            if annofab_account_id is None:
                logger.warning(f"{user_id=} の外部連携情報にAnnofabのaccount_idは設定されていませんでした。")
            af_account_list.append({"user_id": user_id, "annofab_account_id": annofab_account_id})

        df_af_account = pandas.DataFrame(af_account_list)

        df_user = pandas.DataFrame(self.all_organization_members)[["user_id", "username", "organization_member_id"]]

        df = df_user.merge(df_af_account, how="inner", on="user_id")
        return df

    def _get_df_job_and_af_project(self, job_ids: Collection[str]) -> pandas.DataFrame:
        """job_id,annofab_project_idが格納されたpandas.DataFrameを返します。"""
        all_job_dict = {e["job_id"]: e for e in self.all_jobs}

        df_job = pandas.DataFrame(self.all_jobs)

        df_af_project = pandas.DataFrame({"job_id": list(job_ids)})
        df_af_project["annofab_project_id"] = df_af_project["job_id"].apply(
            lambda e: get_annofab_project_id_from_job(all_job_dict[e])
        )

        df = df_job.merge(df_af_project, how="inner", on="job_id")
        return df[["job_id", "job_name", "annofab_project_id"]]

    def _get_af_working_hours_from_af_project(
        self, af_project_id: str, start_date: str, end_date: str
    ) -> list[dict[str, Any]]:
        try:
            logger.debug(
                f"annofab_project_id= '{af_project_id}' のAnnoFabプロジェクトの作業時間を取得します。:: {start_date=}, {end_date=}"
            )
            account_statistics = self.annofab_service.wrapper.get_account_daily_statistics(af_project_id)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == requests.codes.not_found:
                logger.warning(f"annofab_project_id= '{af_project_id}' は存在しません。")
            else:
                logger.warning(f"annofab_project_id= '{af_project_id}' の作業時間を取得できませんでした。:: {e}")
            return []

        result = []
        for account_info in account_statistics:
            af_account_id = account_info["account_id"]
            histories = account_info["histories"]
            for history in histories:
                working_hours = isoduration_to_hour(history["worktime"])
                if working_hours > 0:
                    # TODO 新しい統計webapiに変わったら、ここの条件分岐はなくなる
                    if start_date <= history["date"] <= end_date:
                        result.append(
                            {
                                "annofab_project_id": af_project_id,
                                "annofab_account_id": af_account_id,
                                "date": history["date"],
                                "annofab_working_hours": working_hours,
                            }
                        )
        return result

    def _get_af_working_hours(
        self, af_project_ids: Collection[str], start_date: str, end_date: str
    ) -> pandas.DataFrame:
        """Annofabの作業時間情報が格納されたDataFramaを返す。

        以下の列がある。
        * date
        * annofab_project_id
        * annofab_account_id
        * annofab_working_hours
        """
        result: list[dict[str, Any]] = []

        logger.debug(f"{len(af_project_ids)} 件のAnnoFabプロジェクトの作業時間を取得します。")

        if self.parallelism is not None:
            partial_func = functools.partial(
                self._get_af_working_hours_from_af_project,
                start_date=start_date,
                end_date=end_date,
            )
            with multiprocessing.Pool(self.parallelism) as pool:
                tmp_result = pool.map(partial_func, af_project_ids)
                result = list(itertools.chain.from_iterable(tmp_result))

        else:
            for af_project_id in af_project_ids:
                result.extend(
                    self._get_af_working_hours_from_af_project(af_project_id, start_date=start_date, end_date=end_date)
                )

        if len(result) > 0:
            return pandas.DataFrame(result)
        return pandas.DataFrame(columns=["date", "annofab_project_id", "annofab_account_id", "annofab_working_hours"])

    def _get_df_job_parent_job(self) -> pandas.DataFrame:
        """job_id, parent_job_id, parent_job_nameが格納されたpandas.DataFrameを返します。"""
        all_job_dict = {e["job_id"]: e for e in self.all_jobs}

        df_job = pandas.DataFrame(self.all_jobs)
        df_job["parent_job_id"] = df_job["job_tree"].apply(get_parent_job_id_from_job_tree)

        df_parent_job = pandas.DataFrame({"parent_job_id": df_job["parent_job_id"].unique()})
        df_parent_job["parent_job_name"] = df_parent_job["parent_job_id"].apply(
            lambda e: all_job_dict[e]["job_name"] if e is not None else None
        )

        df = df_job.merge(df_parent_job, how="left", on="parent_job_id")
        return df[["job_id", "parent_job_id", "parent_job_name"]]

    @staticmethod
    def _get_required_columns(is_show_parent_job: bool):
        job_columns = [
            "job_id",
            "job_name",
        ]
        user_columns = [
            "organization_member_id",
            "user_id",
            "username",
        ]
        annofab_columns = ["annofab_project_id", "annofab_account_id", "annofab_working_hours"]

        if is_show_parent_job:
            parent_job_columns = [
                "parent_job_id",
                "parent_job_name",
            ]
            required_columns = (
                ["date"] + job_columns + parent_job_columns + user_columns + ["actual_working_hours"] + annofab_columns
            )
        else:
            required_columns = ["date"] + job_columns + user_columns + ["actual_working_hours"] + annofab_columns

        required_columns.append("notes")
        return required_columns

    def get_df_working_hours(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        job_ids: Optional[Collection[str]] = None,
        user_ids: Optional[Collection[str]] = None,
        is_show_parent_job: bool = False,
    ) -> pandas.DataFrame:
        def _get_start_date(df: pandas.DataFrame) -> str:
            if start_date is None:
                return df["date"].min()
            return min(start_date, df["date"].min())

        def _get_end_date(df: pandas.DataFrame) -> str:
            if end_date is None:
                return df["date"].max()
            return max(end_date, df["date"].max())

        actual_working_hours_daily_list = self.get_actual_working_hours_daily(
            job_ids=job_ids, user_ids=user_ids, start_date=start_date, end_date=end_date
        )

        df_actual_working_hours = pandas.DataFrame(actual_working_hours_daily_list)
        if len(df_actual_working_hours) == 0:
            logger.warning(f"実績作業時間情報が0件でした。")
            return pandas.DataFrame()

        # df_actual_working_hours には含まれていないユーザがAnnofabプロジェクトで作業している可能性があるので、
        # user_id_listが指定された場合は、そのユーザのAnnofabアカウント情報も取得する。
        df_user_and_af_account = self._get_df_user_and_af_account(
            set(df_actual_working_hours["user_id"].unique()) | (set(user_ids) if user_ids is not None else set())
        )

        df_job_and_af_project = self._get_df_job_and_af_project(
            set(df_actual_working_hours["job_id"].unique()) | (set(job_ids) if job_ids is not None else set())
        )

        af_project_ids = [e for e in df_job_and_af_project["annofab_project_id"].unique() if not pandas.isna(e)]
        df_af_working_hours = self._get_af_working_hours(
            af_project_ids=af_project_ids,
            start_date=_get_start_date(df_actual_working_hours),
            end_date=_get_end_date(df_actual_working_hours),
        )

        df = _get_get_df_working_hours_from_df(
            df_actual_working_hours=df_actual_working_hours,
            df_user_and_af_account=df_user_and_af_account,
            df_job_and_af_project=df_job_and_af_project,
            df_af_working_hours=df_af_working_hours,
        )

        if user_ids is not None:
            df = df[df["user_id"].isin(set(user_ids))]

        if is_show_parent_job:
            df_job_parent_job = self._get_df_job_parent_job()
            df = df.merge(df_job_parent_job, how="left", on="job_id")

        df.sort_values(["date", "job_id", "user_id"], inplace=True)
        required_columns = self._get_required_columns(is_show_parent_job)
        return df[required_columns]

    def get_job_id_list_from_parent_job_id_list(self, parent_job_id_list: Collection[str]) -> list[str]:
        return [
            e["job_id"]
            for e in self.all_jobs
            if get_parent_job_id_from_job_tree(e["job_tree"]) in set(parent_job_id_list)
        ]

    def get_job_id_list_from_annofab_project_id_list(self, annofab_project_id_list: list[str]) -> list[str]:
        annofab_project_id_set = set(annofab_project_id_list)

        def _match_job(job: dict[str, Any]) -> bool:
            af_project_id = get_annofab_project_id_from_job(job)
            if af_project_id is None:
                return False
            return af_project_id in annofab_project_id_set

        return [e["job_id"] for e in self.all_jobs if _match_job(e)]


def main(args):

    job_id_list = get_list_from_args(args.job_id)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    annofab_project_id_list = get_list_from_args(args.annofab_project_id)
    user_id_list = get_list_from_args(args.user_id)
    start_date: Optional[str] = args.start_date
    end_date: Optional[str] = args.end_date

    command = " ".join(sys.argv[0:3])
    if all(
        v is None
        for v in [job_id_list, parent_job_id_list, annofab_project_id_list, user_id_list, start_date, end_date]
    ):
        print(f"{command}: error: '--start_date'や'--job_id'などの絞り込み条件を1つ以上指定してください。", file=sys.stderr)
        sys.exit(COMMAND_LINE_ERROR_STATUS_CODE)

    main_obj = ListWorkingHoursWithAnnofab(
        annowork_service=build_annoworkapi(args),
        organization_id=args.organization_id,
        annofab_service=build_annofabapi(),
        parallelism=args.parallelism,
    )

    # job_id, parent_id, annofab_project_id は排他的なので、このような条件分岐を採用した。
    if parent_job_id_list is not None:
        job_id_list = main_obj.get_job_id_list_from_parent_job_id_list(parent_job_id_list)
    elif annofab_project_id_list is not None:
        job_id_list = main_obj.get_job_id_list_from_annofab_project_id_list(annofab_project_id_list)

    df = main_obj.get_df_working_hours(
        start_date=start_date,
        end_date=end_date,
        job_ids=job_id_list,
        user_ids=user_id_list,
        is_show_parent_job=args.show_parent_job,
    )

    if len(df) == 0:
        logger.warning(f"作業時間情報は0件なので、出力しません。")
        return

    logger.info(f"{len(df)} 件の作業時間情報を出力します。")

    if OutputFormat(args.format) == OutputFormat.JSON:
        print_json(df.to_dict("records"), is_pretty=True, output=args.output)
    else:
        print_csv(df, output=args.output)


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
    job_id_group.add_argument("--parent_job_id", type=str, nargs="+", required=False, help="絞り込み対象の親のジョブID")

    job_id_group.add_argument(
        "-af_p",
        "--annofab_project_id",
        type=str,
        nargs="+",
        required=False,
        help="絞り込み対象であるAnnoFabプロジェクトのproject_idを指定してください。",
    )

    parser.add_argument("--start_date", type=str, required=False, help="集計開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=False, help="集計終了日(YYYY-mm-dd)")

    parser.add_argument(
        "--show_parent_job",
        action="store_true",
        help="親のジョブ情報も出力します。",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.add_argument(
        "-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value
    )

    parser.add_argument("--parallelism", type=int, required=False, help="並列度。指定しない場合は、逐次的に処理します。")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list_working_hours"
    subcommand_help = "日ごとの実績作業時間と、ジョブに紐づくAnnoFabプロジェクトの作業時間を一緒に出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
