from __future__ import annotations

import argparse
import datetime
import logging
import subprocess
import tempfile
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
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv

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


def visualize_statistics(temp_dir: Path, args):
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    annofab_project_id_list = get_list_from_args(args.annofab_project_id)
    main_obj = ListLabor(annowork_service, args.organization_id)
    annofab_labor_list = main_obj.get_annofab_labor_list(
        job_id_list=job_id_list,
        annofab_project_id_list=annofab_project_id_list,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    if len(annofab_labor_list) > 0:
        df = pandas.DataFrame(annofab_labor_list)
    else:
        df = pandas.DataFrame(columns=["date", "account_id", "project_id", "actual_worktime_hour"])

    annofab_labor_csv = temp_dir / "annofab_labor.csv"
    print_csv(df, output=annofab_labor_csv)

    command = [
        "annofabcli",
        "statistics",
        "visualize",
        "--output_dir",
        str(args.output_dir),
        "--labor_csv",
        str(annofab_labor_csv),
    ]

    if annofab_project_id_list is not None:
        command.extend(["--project_id"] + annofab_project_id_list)
    elif job_id_list is not None:
        job_id_annofab_project_id_dict = main_obj.get_job_id_annofab_project_id_dict_from_job_id(job_id_list)
        command.extend(["--project_id"] + list(job_id_annofab_project_id_dict.values()))

    if args.user_id is not None:
        command.extend(["--user_id", args.user_id])

    if args.start_date is not None:
        command.extend(["--start_date", args.start_date])

    if args.end_date is not None:
        command.extend(["--end_date", args.end_date])

    if args.task_id is not None:
        command.extend(["--task_id", args.task_id])

    if args.task_query is not None:
        command.extend(["--task_query", args.task_query])

    if args.not_update:
        command.append("--not_update")

    if args.latest:
        command.append("--latest")

    if args.get_task_histories_one_of_each:
        command.append("--get_task_histories_one_of_each")

    if args.minimal:
        command.append("--minimal")

    if args.merge:
        command.append("--merge")

    if args.parallelism is not None:
        command.extend(["--parallelism", str(args.parallelism)])

    str_command = " ".join(command)
    logger.debug(f"run command: {str_command}")
    subprocess.run(command, check=True)


def main(args):
    if args.temp_dir is not None:
        visualize_statistics(args.temp_dir, args)
    else:
        with tempfile.TemporaryDirectory() as str_temp_dir:
            visualize_statistics(Path(str_temp_dir), args)


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

    parser.add_argument("--temp_dir", type=Path, required=False, help="テンポラリディレクトリ")

    # annofabcli statistics visualizeコマンドに渡す引数
    parser.add_argument("-o", "--output_dir", type=Path, required=True, help="[annofabcli] 出力先ディレクトリのパスを指定してください。")

    parser.add_argument(
        "-u",
        "--user_id",
        nargs="+",
        help=(
            "[annofabcli] メンバごとの統計グラフに表示するユーザのuser_idを指定してください。"
            "指定しない場合は、上位20人が表示されます。\n"
            "``file://`` を先頭に付けると、一覧が記載されたファイルを指定できます。"
        ),
    )

    parser.add_argument(
        "-t",
        "--task_id",
        type=str,
        required=False,
        nargs="+",
        help="[annofabcli] 集計対象のタスクのtask_idを指定します。\n" + "``file://`` を先頭に付けると、task_idの一覧が記載されたファイルを指定できます。",
    )

    parser.add_argument(
        "-tq",
        "--task_query",
        type=str,
        help="[annofabcli] タスクの検索クエリをJSON形式で指定します。指定しない場合はすべてのタスクを取得します。\n"
        "``file://`` を先頭に付けると、JSON形式のファイルを指定できます。"
        "クエリのキーは、task_id, phase, phase_stage, status のみです。",
    )

    parser.add_argument(
        "--not_update",
        action="store_true",
        help="[annofabcli] 作業ディレクトリ内のファイルを参照して、統計情報を出力します。" "AnnoFab Web APIへのアクセスを最小限にします。",
    )

    parser.add_argument(
        "--latest",
        action="store_true",
        help="[annofabcli] 統計情報の元になるファイル（アノテーションzipなど）の最新版を参照します。このオプションを指定すると、各ファイルを更新するのに5分以上待ちます。\n"
        "ただしWebAPIの都合上、 'タスク履歴全件ファイル' は最新版を参照できません。タスク履歴の最新版を参照する場合は ``--get_task_histories_one_of_each`` を指定してください。",
    )

    parser.add_argument(
        "--get_task_histories_one_of_each",
        action="store_true",
        help="[annofabcli] タスク履歴を1個ずつ取得して、タスク履歴の最新版を参照します。タスクの数だけWebAPIを実行するので、処理時間が長くなります。",
    )

    parser.add_argument(
        "--minimal",
        action="store_true",
        help="[annofabcli] 必要最小限のファイルを出力します。",
    )

    parser.add_argument(
        "--merge",
        action="store_true",
        help="[annofabcli] 指定した場合、複数のproject_idを指定したときに、マージした統計情報も出力します。ディレクトリ名は ``merge`` です。",
    )

    parser.add_argument(
        "--parallelism",
        type=int,
        help="[annofabcli] 並列度。 ``--project_id`` に複数のproject_idを指定したときのみ有効なオプションです。" "指定しない場合は、逐次的に処理します。",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "visualize_statistics"
    subcommand_help = "AnnoFabの統計情報を実績作業時間と組み合わせて可視化します。"
    description = (
        "AnnoFabの統計情報を実績作業時間と組み合わせて可視化します。\n"
        "``annofabcli statistics visualize`` コマンドのラッパーになります。\n"
        "ドキュメントは https://annofab-cli.readthedocs.io/ja/latest/command_reference/statistics/visualize.html を参照してください。\n"
    )

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=description)
    parse_args(parser)
    return parser
