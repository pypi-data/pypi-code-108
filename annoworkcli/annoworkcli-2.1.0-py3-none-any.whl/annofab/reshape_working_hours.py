from __future__ import annotations

import argparse
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Collection, Optional

import numpy
import pandas
from annofabapi import build as build_annofabapi
from annofabapi.resource import Resource as AnnofabResource
from annoworkapi.job import get_parent_job_id_from_job_tree
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.annofab.list_working_hours import ListWorkingHoursWithAnnofab
from annoworkcli.common.annofab import get_annofab_project_id_from_job
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args
from annoworkcli.common.organization_tag import (
    get_company_from_organization_tag_name,
    is_company_from_organization_tag_name,
)
from annoworkcli.common.utils import print_csv
from annoworkcli.schedule.list_assigned_hours_daily import ListAssignedHoursDaily

logger = logging.getLogger(__name__)


class ShapeType(Enum):
    DETAILS = "details"
    """日毎・人毎の詳細な値を出力する"""

    TOTAL_BY_USER = "total_by_user"
    """人毎に集計作業時間を出力する"""

    TOTAL_BY_PARENT_JOB = "total_by_parent_job"
    """親ジョブ毎に集計した作業時間を出力する"""

    TOTAL_BY_JOB = "total_by_job"
    """ジョブ毎に集計した作業時間を出力する。アサイン対象のジョブと比較できないので、アサイン時間は含まない。"""

    TOTAL = "total"
    """すべてを集計する"""

    LIST_BY_DATE_USER_PARENT_JOB = "list_by_date_user_parent_job"
    """作業時間の一覧を、日付, ユーザ, 親ジョブ単位で出力する。アサイン時間と比較しても意味のある情報にならないので、アサイン時間は含まない。"""

    LIST_BY_DATE_USER_JOB = "list_by_date_user_job"
    """作業時間の一覧を、日付, ユーザ, ジョブ単位で出力する。アサイン対象のジョブと比較できないので、アサイン時間は含まない。"""


def filter_df(
    df: pandas.DataFrame,
    *,
    job_ids: Optional[Collection[str]] = None,
    user_ids: Optional[Collection[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
):
    if start_date is not None:
        df = df[df["date"] >= start_date]

    if end_date is not None:
        df = df[df["date"] <= end_date]

    if user_ids is not None:
        df = df[df["user_id"].isin(set(user_ids))]

    if job_ids is not None:
        df = df[df["job_id"].isin(set(job_ids))]
    return df


class ReshapeDataFrame:
    """
    Args:
        round_decimals: Noneでなければ、数値列を小数点以下 ``round_decimals`` になるように四捨五入する。

    """

    def __init__(self, *, round_decimals: Optional[int] = None) -> None:
        self.round_decimals = round_decimals

    def format_df(self, df: pandas.DataFrame, value_columns: Optional[list[str]] = None) -> pandas.DataFrame:
        df = df.copy()
        if self.round_decimals is not None:
            if value_columns is not None:
                df[value_columns] = df[value_columns].round(self.round_decimals)
            else:
                df = df.round(self.round_decimals)

        return df

    def get_df_total(self, *, df_actual: pandas.DataFrame, df_assigned: pandas.DataFrame) -> pandas.DataFrame:
        """`--shape_type total`に対応するDataFrameを生成する。"""
        df_sum_actual = pandas.DataFrame(df_actual[["actual_working_hours", "annofab_working_hours"]].sum()).T
        df_sum_assigned = pandas.DataFrame(df_assigned[["assigned_working_hours"]].sum()).T

        df = pandas.concat([df_sum_actual, df_sum_assigned], axis=1)

        df.rename(columns={"annofab_working_hours": "monitored_working_hours"}, inplace=True)

        df["activity_rate"] = df["actual_working_hours"] / df["assigned_working_hours"]
        df["activity_diff"] = df["assigned_working_hours"] / df["actual_working_hours"]
        df["monitor_rate"] = df["monitored_working_hours"] / df["actual_working_hours"]
        df["monitor_diff"] = df["actual_working_hours"] - df["monitored_working_hours"]

        return self.format_df(
            df[
                [
                    "assigned_working_hours",
                    "actual_working_hours",
                    "monitored_working_hours",
                    "activity_rate",
                    "activity_diff",
                    "monitor_rate",
                    "monitor_diff",
                ]
            ]
        )

    def get_df_total_by_user(
        self, *, df_actual: pandas.DataFrame, df_assigned: pandas.DataFrame, df_user_company: pandas.DataFrame
    ) -> pandas.DataFrame:
        """`--shape_type total_by_user`に対応するDataFrameを生成する。
        以下の列を持つ
        * user_id
        * username
        * company
        * assigned_working_hours
        * actual_working_hours
        * annofab_working_hours
        * activity_rate
        * activity_diff
        * monitor_rate
        * monitor_diff

        Args:
            df_actual: 実績作業時間とAnnofab作業時間の情報
            df_assigned: アサインされた作業時間の情報
            df_user: ユーザ情報。

        """
        df_sum_actual = df_actual.groupby("user_id")[["actual_working_hours", "annofab_working_hours"]].sum()
        # df_sum_actual が0件のときは、列がないので追加する
        if "actual_working_hours" not in df_sum_actual.columns:
            df_sum_actual["actual_working_hours"] = 0
        if "annofab_working_hours" not in df_sum_actual.columns:
            df_sum_actual["annofab_working_hours"] = 0

        df_sum_assigned = df_assigned.groupby("user_id")[["assigned_working_hours"]].sum()
        # df_sum_assigned が0件のときは、assigned_working_hours 列がないので、追加する。
        if "assigned_working_hours" not in df_sum_assigned.columns:
            df_sum_assigned["assigned_working_hours"] = 0

        df_user = pandas.concat(
            [df_actual.groupby("user_id").first()[["username"]], df_assigned.groupby("user_id").first()[["username"]]]
        ).drop_duplicates()

        df = df_sum_actual.join(df_sum_assigned, how="outer")

        df.fillna(
            {
                "assigned_working_hours": 0,
                "actual_working_hours": 0,
                "annofab_working_hours": 0,
            },
            inplace=True,
        )
        df = df.join(df_user, how="left")

        df.rename(columns={"annofab_working_hours": "monitored_working_hours"}, inplace=True)
        df["activity_rate"] = df["actual_working_hours"] / df["assigned_working_hours"]
        df["activity_diff"] = df["assigned_working_hours"] / df["actual_working_hours"]
        df["monitor_rate"] = df["monitored_working_hours"] / df["actual_working_hours"]
        df["monitor_diff"] = df["actual_working_hours"] - df["monitored_working_hours"]

        df.reset_index(inplace=True)
        df = df.merge(df_user_company[["user_id", "company"]], how="left", on="user_id")

        df.sort_values(by="user_id", key=lambda e: e.str.lower(), inplace=True)
        return self.format_df(
            df[
                [
                    "user_id",
                    "username",
                    "company",
                    "assigned_working_hours",
                    "actual_working_hours",
                    "monitored_working_hours",
                    "activity_rate",
                    "activity_diff",
                    "monitor_rate",
                    "monitor_diff",
                ]
            ]
        )

    def get_df_total_by_job(self, df_actual: pandas.DataFrame) -> pandas.DataFrame:
        """`--shape_type total_by_job`に対応するDataFrameを生成する。

        Notes:
            アサイン時間はparent_jobに対して指定するので、アサイン時間情報は参照しない。
        """

        df_sum_actual = df_actual.groupby("job_id")[["actual_working_hours", "annofab_working_hours"]].sum()
        # df_sum_actual が0件のときは、列がないので追加する
        if "actual_working_hours" not in df_sum_actual.columns:
            df_sum_actual["actual_working_hours"] = 0
        if "annofab_working_hours" not in df_sum_actual.columns:
            df_sum_actual["annofab_working_hours"] = 0

        df_job = df_actual.drop_duplicates(subset=["job_id"])[["job_id", "job_name", "annofab_project_id"]].set_index(
            "job_id"
        )

        df = df_sum_actual.join(df_job, how="left")

        df.fillna(
            {
                "actual_working_hours": 0,
                "annofab_working_hours": 0,
            },
            inplace=True,
        )

        df.rename(columns={"annofab_working_hours": "monitored_working_hours"}, inplace=True)
        df["monitor_rate"] = df["monitored_working_hours"] / df["actual_working_hours"]
        df["monitor_diff"] = df["actual_working_hours"] - df["monitored_working_hours"]

        df.reset_index(inplace=True)
        df.sort_values(by="job_name", key=lambda e: e.str.lower(), inplace=True)

        return self.format_df(
            df[
                [
                    "job_id",
                    "job_name",
                    "annofab_project_id",
                    "actual_working_hours",
                    "monitored_working_hours",
                    "monitor_rate",
                    "monitor_diff",
                ]
            ]
        )

    def get_df_total_by_parent_job(
        self,
        *,
        df_actual: pandas.DataFrame,
        df_assigned: pandas.DataFrame,
        df_job_parent_job: pandas.DataFrame,
        df_parent_job: pandas.DataFrame,
    ) -> pandas.DataFrame:
        """`--shape_type total_by_parent_job`に対応するDataFrameを生成する。"""

        df_tmp_actual = df_actual.merge(df_job_parent_job, how="left", on="job_id", suffixes=("_tmp", None))
        df_sum_actual = df_tmp_actual.groupby("parent_job_id")[["actual_working_hours", "annofab_working_hours"]].sum()
        df_sum_actual.reset_index(inplace=True)
        # df_sum_actual が0件のときは、列がないので追加する
        if "actual_working_hours" not in df_sum_actual.columns:
            df_sum_actual["actual_working_hours"] = 0
        if "annofab_working_hours" not in df_sum_actual.columns:
            df_sum_actual["annofab_working_hours"] = 0

        df_sum_assigned = df_assigned.groupby("job_id")[["assigned_working_hours"]].sum()
        df_sum_assigned.reset_index(inplace=True)
        # df_sum_assigned が0件のときは、assigned_working_hours 列がないので、追加する。
        if "assigned_working_hours" not in df_sum_assigned.columns:
            df_sum_assigned["assigned_working_hours"] = 0

        df = df_sum_actual.merge(df_sum_assigned, how="outer", left_on="parent_job_id", right_on="job_id")
        # outer joinしているので、parent_job_idに欠損値が出る。それをjob_idで埋める。
        df["parent_job_id"].fillna(df["job_id"], inplace=True)

        df = df.merge(df_parent_job, how="left", on="parent_job_id")
        df.fillna(
            {
                "assigned_working_hours": 0,
                "actual_working_hours": 0,
                "annofab_working_hours": 0,
            },
            inplace=True,
        )

        df.rename(columns={"annofab_working_hours": "monitored_working_hours"}, inplace=True)
        df["activity_rate"] = df["actual_working_hours"] / df["assigned_working_hours"]
        df["activity_diff"] = df["assigned_working_hours"] / df["actual_working_hours"]
        df["monitor_rate"] = df["monitored_working_hours"] / df["actual_working_hours"]
        df["monitor_diff"] = df["actual_working_hours"] - df["monitored_working_hours"]

        df.reset_index(inplace=True)
        df.sort_values(by="parent_job_name", key=lambda e: e.str.lower(), inplace=True)

        return self.format_df(
            df[
                [
                    "parent_job_id",
                    "parent_job_name",
                    "assigned_working_hours",
                    "actual_working_hours",
                    "monitored_working_hours",
                    "activity_rate",
                    "activity_diff",
                    "monitor_rate",
                    "monitor_diff",
                ]
            ]
        )

    def get_df_list_by_date_user_parent_job(
        self, df_actual: pandas.DataFrame, df_job_parent_job: pandas.DataFrame, df_parent_job: pandas.DataFrame
    ) -> pandas.DataFrame:
        """`--shape_type list_by_date_user_parent_job`に対応するDataFrameを生成する。"""

        df_tmp_actual = df_actual.merge(df_job_parent_job, how="left", on="job_id", suffixes=("_tmp", None))
        df_sum_actual = df_tmp_actual.groupby(["date", "user_id", "parent_job_id"])[
            ["actual_working_hours", "annofab_working_hours"]
        ].sum()
        df_sum_actual.reset_index(inplace=True)
        # df_sum_actual が0件のときは、列がないので追加する
        if "actual_working_hours" not in df_sum_actual.columns:
            df_sum_actual["actual_working_hours"] = 0
        if "annofab_working_hours" not in df_sum_actual.columns:
            df_sum_actual["annofab_working_hours"] = 0

        df_user = df_actual.drop_duplicates(["user_id", "username"])[["user_id", "username"]]
        df = df_sum_actual.merge(df_user, how="left", on="user_id").merge(df_parent_job, how="left", on="parent_job_id")

        df.fillna(
            {
                "actual_working_hours": 0,
                "annofab_working_hours": 0,
            },
            inplace=True,
        )

        df.rename(columns={"annofab_working_hours": "monitored_working_hours"}, inplace=True)
        df["monitor_rate"] = df["monitored_working_hours"] / df["actual_working_hours"]
        df["monitor_diff"] = df["actual_working_hours"] - df["monitored_working_hours"]

        df.reset_index(inplace=True)
        df.sort_values(by=["date", "user_id", "parent_job_name"], key=lambda e: e.str.lower(), inplace=True)

        return self.format_df(
            df[
                [
                    "date",
                    "user_id",
                    "username",
                    "parent_job_id",
                    "parent_job_name",
                    "actual_working_hours",
                    "monitored_working_hours",
                    "monitor_rate",
                    "monitor_diff",
                ]
            ]
        )

    def get_df_list_by_date_user_job(self, df_actual: pandas.DataFrame) -> pandas.DataFrame:
        """`--shape_type list_by_date_user_job`に対応するDataFrameを生成する。"""
        df = df_actual
        df.rename(columns={"annofab_working_hours": "monitored_working_hours"}, inplace=True)
        df["monitor_rate"] = df["monitored_working_hours"] / df["actual_working_hours"]
        df["monitor_diff"] = df["actual_working_hours"] - df["monitored_working_hours"]
        df.reset_index(inplace=True)
        df.sort_values(by=["date", "user_id", "job_name"], key=lambda e: e.str.lower(), inplace=True)
        return self.format_df(
            df[
                [
                    "date",
                    "user_id",
                    "username",
                    "job_id",
                    "job_name",
                    "annofab_project_id",
                    "actual_working_hours",
                    "monitored_working_hours",
                    "monitor_rate",
                    "monitor_diff",
                    "notes",
                ]
            ],
            value_columns=["actual_working_hours", "monitored_working_hours", "monitor_rate", "monitor_diff"],
        )

    def get_df_details(
        self,
        *,
        df_actual: pandas.DataFrame,
        df_assigned: pandas.DataFrame,
        insert_sum_row: bool = True,
        insert_sum_column: bool = True,
    ) -> pandas.DataFrame:
        """`--shape_type total_by_user`に対応するDataFrameを生成する。
        行方向に日付, 列方向にユーザを並べたDataFrame

        Args:
            insert_sum_row: 合計行を追加する
            insert_sum_column: 合計列を追加する

        """
        SUM_COLUMN_NAME = "総合計"
        SUM_ROW_NAME = "合計"

        # usernameでgroupbyすると同性同名の場合に正しく集計できないので、usernameにuser_idを加えて一意になるようにした。
        df_actual["username"] = df_actual["username"] + "\n" + df_actual["user_id"]
        df_assigned["username"] = df_assigned["username"] + "\n" + df_assigned["user_id"]

        df_sum_actual = df_actual.groupby(["date", "username"])[["actual_working_hours", "annofab_working_hours"]].sum()
        # df_sum_actual が0件のときは、列がないので追加する
        if "actual_working_hours" not in df_sum_actual.columns:
            df_sum_actual["actual_working_hours"] = 0
        if "annofab_working_hours" not in df_sum_actual.columns:
            df_sum_actual["annofab_working_hours"] = 0

        df_sum_assigned = df_assigned.groupby(["date", "username"])[["assigned_working_hours"]].sum()
        # df_sum_assigned が0件のときは、assigned_working_hours 列がないので、追加する。
        if "assigned_working_hours" not in df_sum_assigned.columns:
            df_sum_assigned["assigned_working_hours"] = 0

        df = df_sum_actual.join(df_sum_assigned, how="outer")

        df.fillna(
            {
                "assigned_working_hours": 0,
                "actual_working_hours": 0,
                "annofab_working_hours": 0,
            },
            inplace=True,
        )
        if len(df) == 0:
            return pandas.DataFrame()

        df.rename(columns={"annofab_working_hours": "monitored_working_hours"}, inplace=True)

        if insert_sum_column:
            df_sum_by_date = df.groupby(["date"])[
                ["actual_working_hours", "monitored_working_hours", "assigned_working_hours"]
            ].sum()
            # 列名が"総合計"になるように、indexを変更する
            df_sum_by_date.index = [(date, SUM_COLUMN_NAME) for date in df_sum_by_date.index]

            df = df.append(df_sum_by_date)

        # ヘッダが [user_id, value] になるように設定する
        df2 = df.stack().unstack([1, 2])

        # 日付が連続になるようにする
        not_exists_date_set = {
            str(e.date()) for e in pandas.date_range(start=min(df2.index), end=max(df2.index))
        } - set(df2.index)
        df2 = df2.append([pandas.Series(name=date, dtype="float64") for date in not_exists_date_set], sort=True)
        df2.sort_index(inplace=True)
        # 作業時間がNaNの場合は0に置換する
        df2.replace(
            {
                col: {numpy.nan: 0}
                for col in df2.columns
                if col[1] in ["actual_working_hours", "monitored_working_hours", "assigned_working_hours"]
            },
            inplace=True,
        )

        # user_idの辞書順（大文字小文字区別しない）のユーザのDataFrameを生成する。
        df_user = (
            pandas.concat(
                [
                    df_actual.groupby("user_id").first()[["username"]],
                    df_assigned.groupby("user_id").first()[["username"]],
                ]
            )
            .drop_duplicates()
            .sort_index(key=lambda x: x.str.lower())
        )

        username_list = list(df_user["username"])
        if insert_sum_column:
            username_list = [SUM_COLUMN_NAME] + username_list

        if insert_sum_row:
            # 先頭行に合計を追加する
            tmp_sum_row = df2.sum()
            tmp_sum_row.name = SUM_ROW_NAME
            df2 = pandas.concat([pandas.DataFrame([tmp_sum_row]), df2])

        # activity_rate,monitor_rateの追加。PerformanceWarningが出ないようにするため、まとめて列を追加する
        added_column_list = []
        for username in username_list:
            s1 = pandas.Series(
                df2[(username, "actual_working_hours")] / df2[(username, "assigned_working_hours")],
                name=(username, "activity_rate"),
            )
            s2 = pandas.Series(
                df2[(username, "monitored_working_hours")] / df2[(username, "actual_working_hours")],
                name=(username, "monitor_rate"),
            )
            added_column_list.extend([s1, s2])

        df_added_rate = pandas.concat(added_column_list, axis="columns")
        df2 = pandas.concat([df2, df_added_rate], axis="columns")

        df2 = self.format_df(df2)

        df2 = df2[
            [
                (m, v)
                for m in username_list
                for v in [
                    "assigned_working_hours",
                    "actual_working_hours",
                    "monitored_working_hours",
                    "activity_rate",
                    "monitor_rate",
                ]
            ]
        ]

        # date列を作る
        df2.reset_index(inplace=True)
        return df2


def get_dataframe_from_input_file(input_file: Path) -> pandas.DataFrame:
    """JSONまたはCSVファイルからDataFrameを生成する
    拡張子がjsonかcsvかで読み込み方法を変更する。

    Args:
        input_file (Path): [description]

    Returns:
        list[dict[str,Any]]: [description]
    """
    if input_file.suffix.lower() == ".json":
        with input_file.open() as f:
            tmp = json.load(f)
            return pandas.DataFrame(tmp)

    elif input_file.suffix.lower() == ".csv":
        return pandas.read_csv(str(input_file))

    return pandas.DataFrame()


class ReshapeWorkingHours:
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
        self.all_jobs = self.annowork_service.api.get_jobs(self.organization_id)
        self.list_actual_obj = ListWorkingHoursWithAnnofab(
            annowork_service=annowork_service,
            organization_id=organization_id,
            annofab_service=annofab_service,
            parallelism=parallelism,
        )
        self.list_assigned_obj = ListAssignedHoursDaily(
            annowork_service=annowork_service, organization_id=organization_id
        )

    def get_job_id_list_from_af_project_id(self, annofab_project_id_list: list[str]) -> list[str]:
        annofab_project_id_set = set(annofab_project_id_list)

        def _match_job(job: dict[str, Any]) -> bool:
            af_project_id = get_annofab_project_id_from_job(job)
            if af_project_id is None:
                return False
            return af_project_id in annofab_project_id_set

        return [e["job_id"] for e in self.all_jobs if _match_job(e)]

    def get_df_actual(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user_ids: Collection[str] = None,
        parent_job_ids: Collection[str] = None,
        job_ids: Collection[str] = None,
    ):
        """実績作業時間とannofab作業時間を比較したDataFrameを取得する。

        parent_job_ids, job_ids, annofab_project_ids, は排他的
        Returns:
            [type]: [description]
        """
        if parent_job_ids is not None:
            job_ids = self.list_actual_obj.get_job_id_list_from_parent_job_id_list(parent_job_ids)

        df = self.list_actual_obj.get_df_working_hours(
            start_date=start_date, end_date=end_date, job_ids=job_ids, user_ids=user_ids
        )
        return df

    def get_df_assigned(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        parent_job_ids: Collection[str] = None,
        user_ids: Collection[str] = None,
    ):
        result = self.list_assigned_obj.get_assigned_hours_daily_list(
            start_date=start_date,
            end_date=end_date,
            job_ids=parent_job_ids,
            user_ids=user_ids,
        )
        return pandas.DataFrame(result)

    def get_df_user_company(self) -> pandas.DataFrame:
        tags = self.annowork_service.api.get_organization_tags(self.organization_id)
        company_tags = [e for e in tags if is_company_from_organization_tag_name(e["organization_tag_name"])]
        result = []
        for tag in company_tags:
            tmp_list = self.annowork_service.api.get_organization_tag_members(
                self.organization_id, tag["organization_tag_id"]
            )
            for member in tmp_list:
                member["company"] = get_company_from_organization_tag_name(tag["organization_tag_name"])
            result.extend(tmp_list)

        df = pandas.DataFrame(result)[["user_id", "username", "company"]]
        df_duplicated = df[df.duplicated(subset=["user_id"])]
        if len(df_duplicated) > 0:
            logger.warning(f"{len(df_duplicated)} 件のユーザに複数の会社情報が組織タグとして設定されています。:: {list(df_duplicated['user_id'])}")
            df = df.drop_duplicates(subset=["user_id"])
        return df

    def get_df_job_parent_job(self) -> pandas.DataFrame:
        """job_id,parent_job_idが格納されたpandas.DataFrameを返します。"""
        df_job = pandas.DataFrame(self.all_jobs)
        df_job["parent_job_id"] = df_job["job_tree"].apply(get_parent_job_id_from_job_tree)

        df_parent_job = pandas.DataFrame({"parent_job_id": df_job["parent_job_id"].unique()})

        df = df_job.merge(df_parent_job, how="left", on="parent_job_id")
        return df[["job_id", "parent_job_id"]]

    def get_df_parent_job(self) -> pandas.DataFrame:
        """parent_job_id, parent_job_nameが格納されたpandas.DataFrameを返します。"""
        df_job = pandas.DataFrame(self.all_jobs)
        df_job["is_parent"] = df_job["job_tree"].apply(lambda e: get_parent_job_id_from_job_tree(e) is None)

        df = df_job[df_job["is_parent"]][["job_id", "job_name"]]
        df.rename(columns={"job_name": "parent_job_name", "job_id": "parent_job_id"}, inplace=True)
        return df

    def get_df_output(
        self, df_actual: pandas.DataFrame, df_assigned: pandas.DataFrame, shape_type: ShapeType
    ) -> pandas.DataFrame:

        reshape_obj = ReshapeDataFrame(round_decimals=2)
        if shape_type == ShapeType.DETAILS:
            df_output = reshape_obj.get_df_details(df_actual=df_actual, df_assigned=df_assigned)

        elif shape_type == ShapeType.TOTAL_BY_USER:
            df_user_company = self.get_df_user_company()
            df_output = reshape_obj.get_df_total_by_user(
                df_actual=df_actual, df_assigned=df_assigned, df_user_company=df_user_company
            )

        elif shape_type == ShapeType.TOTAL_BY_JOB:
            df_output = reshape_obj.get_df_total_by_job(df_actual=df_actual)

        elif shape_type == ShapeType.TOTAL_BY_PARENT_JOB:
            df_job_parent_job = self.get_df_job_parent_job()
            df_parent_job = self.get_df_parent_job()
            df_output = reshape_obj.get_df_total_by_parent_job(
                df_actual=df_actual,
                df_assigned=df_assigned,
                df_job_parent_job=df_job_parent_job,
                df_parent_job=df_parent_job,
            )

        elif shape_type == ShapeType.TOTAL:
            df_output = reshape_obj.get_df_total(df_actual=df_actual, df_assigned=df_assigned)

        elif shape_type == ShapeType.LIST_BY_DATE_USER_JOB:
            df_output = reshape_obj.get_df_list_by_date_user_job(df_actual=df_actual)

        elif shape_type == ShapeType.LIST_BY_DATE_USER_PARENT_JOB:
            df_job_parent_job = self.get_df_job_parent_job()
            df_parent_job = self.get_df_parent_job()
            df_output = reshape_obj.get_df_list_by_date_user_parent_job(
                df_actual=df_actual, df_job_parent_job=df_job_parent_job, df_parent_job=df_parent_job
            )

        else:
            df_output = pandas.DataFrame
        return df_output

    def filter_df(
        self,
        *,
        df_actual: pandas.DataFrame,
        df_assigned: pandas.DataFrame,
        parent_job_ids: Optional[Collection[str]] = None,
        job_ids: Optional[Collection[str]] = None,
        user_ids: Optional[Collection[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> tuple[pandas.DataFrame, pandas.DataFrame]:
        """df_actual, df_assigned を絞り込みます。


        Args:
            parent_job_ids: df_actualのjob_idの親ジョブのjob_id, df_assignedのjob_idで絞り込みます。
            job_ids: df_actualのjob_idで絞り込みます。df_assignedは絞り込まず0件のDataFrameになります。

        Returns:
            tuple[pandas.DataFrame, pandas.DataFrame]: 絞り込まれたdf_actual, df_assigned
        """
        child_job_ids: Optional[Collection] = None
        if parent_job_ids is not None:
            child_job_ids = {
                e["job_id"]
                for e in self.all_jobs
                if get_parent_job_id_from_job_tree(e["job_tree"]) in set(parent_job_ids)
            }
            df_actual = filter_df(
                df_actual, job_ids=child_job_ids, user_ids=user_ids, start_date=start_date, end_date=end_date
            )
        else:
            df_actual = filter_df(
                df_actual, job_ids=job_ids, user_ids=user_ids, start_date=start_date, end_date=end_date
            )

        if job_ids is not None:
            # アサインは親ジョブに紐付けているため、job_idに対応するアサインはない。したがって、0件にする。
            df_assigned = pandas.DataFrame(columns=df_assigned.columns)
        else:
            # df_assignedのjob_idがparent_job_idになるので、job_ids にはparent_job_idsを渡している
            df_assigned = filter_df(
                df_assigned, job_ids=parent_job_ids, user_ids=user_ids, start_date=start_date, end_date=end_date
            )
        return (df_actual, df_assigned)


def get_empty_df_actual() -> pandas.DataFrame:
    return pandas.DataFrame(
        columns=[
            "date",
            "job_id",
            "job_name",
            "organization_member_id",
            "user_id",
            "username",
            "actual_working_hours",
            "annofab_project_id",
            "annofab_account_id",
            "annofab_working_hours",
        ]
    )


def get_empty_df_assigned() -> pandas.DataFrame:
    return pandas.DataFrame(
        columns=[
            "date",
            "job_id",
            "job_name",
            "organization_member_id",
            "user_id",
            "username",
            "assigned_working_hours",
        ]
    )


def main(args):
    main_obj = ReshapeWorkingHours(
        annowork_service=build_annoworkapi(args),
        organization_id=args.organization_id,
        annofab_service=build_annofabapi(),
        parallelism=args.parallelism,
    )

    parent_job_id_list = get_list_from_args(args.parent_job_id)
    job_id_list = get_list_from_args(args.job_id)
    annofab_project_id_list = get_list_from_args(args.annofab_project_id)
    # "--job_id"と"--annofab_project_id"は排他的なので、job_id_listは上書きする
    if annofab_project_id_list is not None:
        job_id_list = main_obj.get_job_id_list_from_af_project_id(annofab_project_id_list)

    user_id_list = get_list_from_args(args.user_id)
    start_date = args.start_date
    end_date = args.end_date

    shape_type = ShapeType(args.shape_type)

    if args.actual_file is not None:

        df_actual = get_dataframe_from_input_file(args.actual_file)
    else:
        df_actual = main_obj.get_df_actual(
            start_date=start_date,
            end_date=end_date,
            parent_job_ids=parent_job_id_list,
            job_ids=job_id_list,
            user_ids=user_id_list,
        )
        if len(df_actual) == 0:
            df_actual = get_empty_df_actual()

    if args.assigned_file is not None:
        df_assigned = get_dataframe_from_input_file(args.assigned_file)
    else:
        if (
            shape_type
            in {
                ShapeType.TOTAL_BY_JOB,
                ShapeType.LIST_BY_DATE_USER_JOB,
                ShapeType.LIST_BY_DATE_USER_PARENT_JOB,
            }
            or job_id_list is not None
        ):
            # このshape_typeのときは、df_assignedが不要なので、空のDataFrameを生成する
            # job_idが指定されたときも、アサインを取得できないので、空のDataFrameを生成する
            df_assigned = get_empty_df_assigned()
        else:
            df_assigned = main_obj.get_df_assigned(
                start_date=start_date, end_date=end_date, parent_job_ids=parent_job_id_list, user_ids=user_id_list
            )
            if len(df_assigned) == 0:
                df_assigned = get_empty_df_assigned()

    df_actual, df_assigned = main_obj.filter_df(
        df_actual=df_actual,
        df_assigned=df_assigned,
        start_date=args.start_date,
        end_date=args.end_date,
        user_ids=user_id_list,
        parent_job_ids=parent_job_id_list,
        job_ids=job_id_list,
    )

    df_output = main_obj.get_df_output(df_actual=df_actual, df_assigned=df_assigned, shape_type=shape_type)

    if len(df_output) == 0:
        logger.warning(f"出力対象のデータは0件なので、出力しません。")
        return
    print_csv(df_output, output=args.output)


def parse_args(parser: argparse.ArgumentParser):

    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    parser.add_argument(
        "--actual_file",
        type=Path,
        required=False,
        help="``annoworkcli annofab list_working_hours`` コマンドで出力したファイルのパスを指定します。"
        "未指定の場合は ``annoworkcli annofab list_working_hours`` コマンドの結果を参照します。",
    )

    parser.add_argument(
        "--assigned_file",
        type=Path,
        required=False,
        help="``annoworkcli schedule list_daily`` コマンドで出力したファイルのパスを指定します。"
        "未指定の場合は ``annoworkcli schedule list_daily`` コマンドの結果を参照します。",
    )

    parser.add_argument("-u", "--user_id", type=str, nargs="+", required=False, help="絞り込み対象のユーザID")

    # parent_job_idとjob_idの両方を指定するユースケースはなさそうなので、exclusiveにする。
    job_id_group = parser.add_mutually_exclusive_group()
    job_id_group.add_argument(
        "-pj",
        "--parent_job_id",
        type=str,
        nargs="+",
        required=False,
        help="絞り込み対象の親のジョブID。\n" "指定すると、actual_fileのjob_idの親ジョブ、assigned_fileのjob_idで絞り込まれます。",
    )
    job_id_group.add_argument(
        "-j",
        "--job_id",
        type=str,
        nargs="+",
        help="指定すると、actual_fileのjob_idで絞り込まれます。assigned_fileに対応するジョブはないので、assigned_fileは参照されません。",
    )

    job_id_group.add_argument(
        "-af_p",
        "--annofab_project_id",
        type=str,
        nargs="+",
        help="指定すると、actual_fileのjob_idに紐づくAnnofabのproject_idで絞り込まれます。assigned_fileに対応するジョブはないので、assigned_fileは参照されません。",
    )

    parser.add_argument("--start_date", type=str, required=False, help="集計開始日(YYYY-mm-dd)")
    parser.add_argument("--end_date", type=str, required=False, help="集計終了日(YYYY-mm-dd)")

    shape_type_choices = [e.value for e in ShapeType]
    parser.add_argument(
        "--shape_type",
        type=str,
        required=True,
        choices=shape_type_choices,
        help=(
            "CSVの成形タイプを指定します。\n"
            "\n"
            "* details: 日付ごとユーザごとに作業時間を集計します。 \n"
            "* total_by_user: ユーザごとに作業時間を集計します。 \n"
            "* total_by_job: ジョブごとに作業時間を集計します。 ``--assigned_file`` は不要です。 \n"
            "* total_by_parent_job: 親ジョブごとに作業時間を集計します。 \n"
            "* total: 作業時間を合計します。 \n"
            "* list_by_date_user_job: 作業時間の一覧を日付、ユーザ、ジョブ単位で出力します。 ``--assigned_file`` は不要です。 \n"
            "* list_by_date_user_parent_job: 作業時間の一覧を日付、ユーザ、親ジョブ単位で出力します。 ``--assigned_file`` は不要です。 \n"
        ),
    )

    parser.add_argument("--parallelism", type=int, required=False, help="並列度。指定しない場合は、逐次的に処理します。")

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "reshape_working_hours"
    subcommand_help = "AnnoWorkの実績作業時間とアサイン時間、Annofabの作業時間を比較できるようなCSVファイルに成形します。"
    description = (
        "AnnoWorkの実績作業時間とアサイン時間、Annofabの作業時間を比較できるようなCSVファイルに成形します。\n"
        "レポートとして利用できるようにするため、以下を対応しています。\n"
        " * 小数点以下2桁目まで表示\n"
        " * 比較対象の比率と差分を表示\n"
        " * organization_member_idなどGUIに直接関係ない項目は表示しない\n"
    )

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=description)
    parse_args(parser)
    return parser
