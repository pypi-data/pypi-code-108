from __future__ import annotations

import argparse
import datetime
import itertools
import json
import logging
import subprocess
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Collection, Dict, List, Optional, Tuple

import dateutil
import more_itertools
import pandas
from annofabapi import build as build_annofabapi
from annofabapi.models import Task
from annofabapi.resource import Resource as AnnofabResource
from annofabapi.utils import str_now
from annofabcli.statistics.summarize_task_count_by_task_id import TaskStatusForSummary
from annoworkapi.resource import Resource as AnnoworkResource
from dataclasses_json import DataClassJsonMixin
from dateutil.parser import parse
from more_itertools import first_true

import annoworkcli
from annoworkcli.common.annofab import get_annofab_project_id_from_job
from annoworkcli.common.cli import build_annoworkapi
from annoworkcli.common.utils import isoduration_to_hour, print_json

logger = logging.getLogger(__name__)

ActualWorktimeDict = Dict[str, float]
"""keyがdate, valueが実績作業時間のdict"""


@dataclass
class TaskPhaseStatistics(DataClassJsonMixin):
    date: str
    annotation_worktime: float = 0
    inspection_worktime: float = 0
    acceptance_worktime: float = 0

    def sum_worktime(self) -> float:
        return self.annotation_worktime + self.inspection_worktime + self.acceptance_worktime


@dataclass
class MonitoredWorktime(DataClassJsonMixin):
    """AnnoFab計測時間の詳細情報"""

    sum: float
    """合計時間[hour]"""
    annotation: float
    inspection: float
    acceptance: float


@dataclass
class RemainingTaskCount(DataClassJsonMixin):
    """
    フェーズごとのタスク数
    """

    complete: int = 0
    """完了状態のタスク数"""

    annotation_not_started: int = 0
    """一度も教師付作業されていないタスク数"""

    inspection_not_started: int = 0
    """一度も検査作業されていないタスク数"""

    acceptance_not_started: int = 0
    """一度も受入作業されていないタスク数"""

    on_hold: int = 0
    """保留状態のタスク数"""

    other: int = 0
    """休憩中/作業中/2回目以降の各フェーズの未着手状態のタスク数"""


@dataclass
class ProgressData(DataClassJsonMixin):
    # task_count: TaskCount
    # """タスク数情報"""

    actual_worktime: float
    """実績作業時間[hour]"""

    task_count: int
    """完了したタスク数"""

    input_data_count: int
    """完了したタスク配下の入力データ数"""

    velocity_per_task: Optional[float]
    """actual_worktime/task_count"""

    velocity_per_input_data: Optional[float]
    """actual_worktime/input_data_count"""

    monitored_worktime: Optional[float] = None
    """AnnoFabの計測作業時間[hour]"""

    annotation_monitored_worktime: Optional[float] = None
    """AnnoFabのannotation計測作業時間[hour]"""

    inspection_monitored_worktime: Optional[float] = None
    """AnnoFabのinspection計測作業時間[hour]"""

    acceptance_monitored_worktime: Optional[float] = None
    """AnnoFabのacceptance計測作業時間[hour]"""


@dataclass
class ResultValues(DataClassJsonMixin):

    cumulation: ProgressData
    """累計情報"""
    today: ProgressData
    """対象日当日の情報"""
    week: ProgressData
    """対象日から1週間（直前7日間）の情報"""


@dataclass
class DashboardData(DataClassJsonMixin):
    job_ids: List[str]
    annofab_project_id: str
    annofab_project_title: str
    date: str
    """対象日（YYYY-MM-DD）"""
    measurement_datetime: str
    """計測日時。（2004-04-01T12:00+09:00形式）"""

    remaining_task_count: RemainingTaskCount
    """残りのタスク数"""
    result: ResultValues


def add_info_to_task(task: Task):
    task["status_for_summary"] = TaskStatusForSummary.from_task(task).value


def get_remaining_task_count_info_from_task_list(task_list: List[Task]) -> RemainingTaskCount:
    """
    状態ごとのタスク数を取得する。

    Args:
        task_list:

    Returns:

    """
    status_list: List[str] = [e["status_for_summary"] for e in task_list]
    tmp = pandas.Series.value_counts(status_list)
    task_count = RemainingTaskCount.from_dict(tmp.to_dict())
    return task_count


def get_completed_task_count_and_input_data_count(task_list: List[Task]) -> Tuple[int, int]:
    """
    完了したタスク数と入力データ数を求める

    Args:
        task_list:

    Returns:
        Tuple[task_count, input_data_count]
    """
    task_list = [e for e in task_list if e["status_for_summary"] == TaskStatusForSummary.COMPLETE.value]
    input_data_count = len(list(itertools.chain.from_iterable([e["input_data_id_list"] for e in task_list])))
    task_count = len(task_list)
    return task_count, input_data_count


def _to_datetime_from_date(date: datetime.date) -> datetime.datetime:
    dt = datetime.datetime.combine(date, datetime.datetime.min.time())
    return dt.replace(tzinfo=dateutil.tz.tzlocal())


def millisecond_to_hour(millisecond: int):
    return millisecond / 1000 / 3600


def get_task_list_where_updated_datetime(
    task_list: List[Task], lower_date: datetime.date, upper_date: datetime.date
) -> List[Task]:
    """
    タスクの更新日が、対象期間内であるタスク一覧を取得する。

    Args:
        task_list:
        lower_date:
        upper_date:

    Returns:

    """

    def pred(task):
        updated_datetime = parse(task["updated_datetime"])
        return lower_datetime <= updated_datetime < upper_datetime

    lower_datetime = _to_datetime_from_date(lower_date)
    upper_datetime = _to_datetime_from_date(upper_date + datetime.timedelta(days=1))
    return [t for t in task_list if pred(t)]


def _get_today_info(
    today: str,
    task_list: List[Task],
    actual_worktime_dict: Dict[str, float],
    task_phase_statistics: List[TaskPhaseStatistics],
) -> ProgressData:
    dt_today = datetime.datetime.strptime(today, "%Y-%m-%d").date()
    task_list_for_day = get_task_list_where_updated_datetime(task_list, lower_date=dt_today, upper_date=dt_today)
    today_monitor_worktime_info = get_monitored_worktime(
        task_phase_statistics, lower_date=dt_today, upper_date=dt_today
    )
    task_count, input_data_count = get_completed_task_count_and_input_data_count(task_list_for_day)
    actual_worktime = actual_worktime_dict.get(today, 0)
    today_info = ProgressData(
        task_count=task_count,
        input_data_count=input_data_count,
        actual_worktime=actual_worktime,
        velocity_per_task=actual_worktime / task_count if task_count > 0 else None,
        velocity_per_input_data=actual_worktime / input_data_count if input_data_count > 0 else None,
    )
    if today_monitor_worktime_info is not None:
        today_info.monitored_worktime = today_monitor_worktime_info.sum
        today_info.annotation_monitored_worktime = today_monitor_worktime_info.annotation
        today_info.inspection_monitored_worktime = today_monitor_worktime_info.inspection
        today_info.acceptance_monitored_worktime = today_monitor_worktime_info.acceptance
    return today_info


def _get_week_info(
    today: str,
    task_list: List[Task],
    actual_worktime_dict: Dict[str, float],
    task_phase_statistics: List[TaskPhaseStatistics],
) -> ProgressData:
    dt_today = datetime.datetime.strptime(today, "%Y-%m-%d").date()
    week_ago = dt_today - datetime.timedelta(days=6)
    task_list_for_week = get_task_list_where_updated_datetime(task_list, lower_date=week_ago, upper_date=dt_today)
    week_monitor_worktime_info = get_monitored_worktime(task_phase_statistics, lower_date=week_ago, upper_date=dt_today)
    task_count, input_data_count = get_completed_task_count_and_input_data_count(task_list_for_week)
    actual_worktime = get_worktime_for_period(actual_worktime_dict, lower_date=week_ago, upper_date=dt_today)

    seven_days_info = ProgressData(
        task_count=task_count,
        input_data_count=input_data_count,
        actual_worktime=actual_worktime,
        velocity_per_task=actual_worktime / task_count if task_count > 0 else None,
        velocity_per_input_data=actual_worktime / input_data_count if input_data_count > 0 else None,
    )
    if week_monitor_worktime_info is not None:
        seven_days_info.monitored_worktime = week_monitor_worktime_info.sum
        seven_days_info.annotation_monitored_worktime = week_monitor_worktime_info.annotation
        seven_days_info.inspection_monitored_worktime = week_monitor_worktime_info.inspection
        seven_days_info.acceptance_monitored_worktime = week_monitor_worktime_info.acceptance
    return seven_days_info


def get_worktime_for_period(worktime_dict: Dict[str, float], lower_date: datetime.date, upper_date: datetime.date):
    sum_worktime = 0.0
    for dt in pandas.date_range(start=lower_date, end=upper_date):
        str_date = str(dt.date())
        sum_worktime += worktime_dict.get(str_date, 0.0)
    return sum_worktime


def get_monitored_worktime(
    task_phase_statistics: List[TaskPhaseStatistics], lower_date: datetime.date, upper_date: datetime.date
) -> Optional[MonitoredWorktime]:
    upper_stat = first_true(task_phase_statistics, pred=lambda e: e.date == str(upper_date))
    lower_stat = first_true(
        task_phase_statistics, pred=lambda e: e.date == str(lower_date - datetime.timedelta(days=1))
    )
    if upper_stat is None or lower_stat is None:
        logger.debug(f"{lower_date} 〜 {upper_date} 期間のmonitor_worktimeを算出できませんでした。")
        return None

    return MonitoredWorktime(
        sum=upper_stat.sum_worktime() - lower_stat.sum_worktime(),
        annotation=upper_stat.annotation_worktime - lower_stat.annotation_worktime,
        inspection=upper_stat.inspection_worktime - lower_stat.inspection_worktime,
        acceptance=upper_stat.acceptance_worktime - lower_stat.acceptance_worktime,
    )


def _get_cumulation_info(task_list: List[Task], actual_worktime_dict: Dict[str, float]) -> ProgressData:
    task_count, input_data_count = get_completed_task_count_and_input_data_count(task_list)
    actual_worktime = sum(actual_worktime_dict.values())

    return ProgressData(
        task_count=task_count,
        input_data_count=input_data_count,
        monitored_worktime=sum([t["worktime_hour"] for t in task_list]),
        actual_worktime=actual_worktime,
        velocity_per_task=actual_worktime / task_count if task_count > 0 else None,
        velocity_per_input_data=actual_worktime / input_data_count if input_data_count > 0 else None,
    )


def create_result_values(
    actual_worktime_dict: ActualWorktimeDict,
    task_phase_statistics: list[TaskPhaseStatistics],
    date: str,
    task_list: List[Task],
) -> ResultValues:
    """
    実績情報を生成する。

    Args:
        task_list:
        date: タスク数 集計対象日

    Returns:

    """
    for task in task_list:
        task["status_for_summary"] = TaskStatusForSummary.from_task(task).value
        task["worktime_hour"] = millisecond_to_hour(task["work_time_span"])

    cumulation_info = _get_cumulation_info(task_list, actual_worktime_dict)
    today_info = _get_today_info(
        today=date,
        task_list=task_list,
        actual_worktime_dict=actual_worktime_dict,
        task_phase_statistics=task_phase_statistics,
    )
    week_info = _get_week_info(
        today=date,
        task_list=task_list,
        actual_worktime_dict=actual_worktime_dict,
        task_phase_statistics=task_phase_statistics,
    )
    return ResultValues(cumulation=cumulation_info, today=today_info, week=week_info)


class GetDashboard:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str, annofab_service: AnnofabResource):
        self.annowork_service = annowork_service
        self.organization_id = organization_id
        self.annofab_service = annofab_service
        self.all_jobs = self.annowork_service.api.get_jobs(self.organization_id)

    def get_task_phase_statistics(self, project_id: str) -> List[TaskPhaseStatistics]:
        """
        フェーズごとの累積作業時間をCSVに出力するための dict 配列を作成する。

        Args:
            project_id:

        Returns:
            フェーズごとの累積作業時間に対応するdict配列

        """
        task_phase_statistics = self.annofab_service.wrapper.get_phase_daily_statistics(project_id)
        row_list: List[TaskPhaseStatistics] = []
        for stat_by_date in task_phase_statistics:
            elm = {"date": stat_by_date["date"]}
            for phase_stat in stat_by_date["phases"]:
                phase = phase_stat["phase"]
                worktime_hour = isoduration_to_hour(phase_stat["worktime"])
                elm[f"{phase}_worktime"] = worktime_hour
            row_list.append(TaskPhaseStatistics.from_dict(elm))
        return row_list

    def get_actual_worktime_dict(self, job_ids: Collection[str], date: str) -> ActualWorktimeDict:
        """
        日毎のプロジェクト全体の実績作業時間を取得する。

        Args:
            project_id:
            date: 対象期間の終了日

        Returns:
            key:date, value:実績作業時間のdict

        """

        actual_daily_list = []
        for job_id in job_ids:
            actual_daily_list.extend(
                self.annowork_service.wrapper.get_actual_working_times_daily(
                    self.organization_id, job_id=job_id, term_end_date=date
                )
            )

        actual_worktime_dict: Dict[str, float] = defaultdict(float)
        for actual in actual_daily_list:
            actual_worktime_dict[actual["date"]] += actual["actual_working_hours"]

        return actual_worktime_dict

    def create_dashboard_data(
        self, job_ids: list[str], af_project_id: str, date: str, task_list: List[Task]
    ) -> DashboardData:
        project = self.annofab_service.wrapper.get_project_or_none(af_project_id)
        if project is None:
            raise RuntimeError(f"annofabのproject_id='{af_project_id}' にアクセスできませんでした。")

        actual_worktime_dict = self.get_actual_worktime_dict(job_ids, date)
        task_phase_statistics = self.get_task_phase_statistics(af_project_id)

        result = create_result_values(
            actual_worktime_dict=actual_worktime_dict,
            task_phase_statistics=task_phase_statistics,
            date=date,
            task_list=task_list,
        )
        remaining_task_count = get_remaining_task_count_info_from_task_list(task_list)

        dashboard_info = DashboardData(
            job_ids=job_ids,
            annofab_project_id=af_project_id,
            annofab_project_title=project["title"],
            date=date,
            measurement_datetime=str_now(),
            remaining_task_count=remaining_task_count,
            result=result,
        )
        return dashboard_info

    def get_job_id_list_from_af_project_id(self, annofab_project_id: str) -> list[str]:
        def _match_job(job: dict[str, Any]) -> bool:
            af_project_id = get_annofab_project_id_from_job(job)
            if af_project_id is None:
                return False
            return af_project_id == annofab_project_id

        return [e["job_id"] for e in self.all_jobs if _match_job(e)]

    def get_af_project_id_from_job_id(self, job_id: str) -> Optional[str]:
        job = more_itertools.first_true(self.all_jobs, pred=lambda e: e["job_id"] == job_id)
        if job is None:
            return None

        return get_annofab_project_id_from_job(job)


def execute_annofabcli_project_download(annofab_project_id: str, output_file: Path, is_latest: bool):
    command = [
        "annofabcli",
        "project",
        "download",
        "task",
        "--project_id",
        annofab_project_id,
        "--output",
        str(output_file),
    ]
    if is_latest:
        command.append("--latest")

    str_command = " ".join(command)
    logger.debug(f"run command: {str_command}")
    subprocess.run(command, check=True)


def main(args):
    main_obj = GetDashboard(
        annowork_service=build_annoworkapi(args),
        organization_id=args.organization_id,
        annofab_service=build_annofabapi(),
    )

    # args.job_idとargs.annofab_project_idの必ずどちらかは設定されている
    if args.job_id is not None:
        job_id = args.job_id
        af_project_id = main_obj.get_af_project_id_from_job_id(job_id)
        logger.debug(f"{job_id=}に紐づくAnnofabのproject_id={af_project_id}")
        if af_project_id is None:
            logger.error(f"{job_id=}に紐づくAnnofabのproject_idを取得できないので、処理を終了します。")
            return
        job_id_list = [job_id]

    elif args.annofab_project_id is not None:
        af_project_id = args.annofab_project_id
        assert af_project_id is not None
        # annofabのプロジェクトに紐づくジョブは複数あるので、job_id_listを採用する
        job_id_list = main_obj.get_job_id_list_from_af_project_id(af_project_id)
        logger.debug(f"{af_project_id=}に紐づくAnnoworkのjob_ids={job_id_list}")

    else:
        logger.error(f"--job_idまたは--annofab_project_idのどちらかを必ず指定してください。")
        return

    if args.annofab_task_json is not None:
        with open(args.annofab_task_json, encoding="utf-8") as f1:
            task_list = json.load(f1)

    else:
        with tempfile.NamedTemporaryFile() as f2:
            execute_annofabcli_project_download(af_project_id, output_file=Path(f2.name), is_latest=args.latest)
            task_list = json.load(f2)

    dashboard_data = main_obj.create_dashboard_data(
        job_ids=job_id_list, af_project_id=af_project_id, date=args.date, task_list=task_list
    )
    print_json(dashboard_data.to_dict(), is_pretty=True, output=args.output)


def parse_args(parser: argparse.ArgumentParser):

    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    job_group = parser.add_mutually_exclusive_group(required=True)
    job_group.add_argument(
        "-j",
        "--job_id",
        type=str,
        help="出力対象ジョブのjob_id",
    )
    job_group.add_argument(
        "-af_p",
        "--annofab_project_id",
        type=str,
        help="出力対象ジョブに紐づくAnnofabプロジェクトのproject_id",
    )

    parser.add_argument("--date", type=str, required=True, help="``YYYY-MM-DD`` 形式で実績の対象日を指定してください。")

    parser.add_argument(
        "--annofab_task_json",
        type=str,
        help="Annofabのタスク全件ファイルのパスを指定します。指定しない場合は、``$ annofabcli project download task`` コマンドの出力結果を参照します。",
    )

    parser.add_argument(
        "--latest",
        action="store_true",
        help="指定した場合、 ``$ annofabcli project download task`` コマンドに ``--latest`` を指定します。",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "get_dashboard"
    subcommand_help = "ダッシュボードとなる情報（タスク数など）をJSON形式で出力します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
