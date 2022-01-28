from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.actual_working_time.list_actual_working_time import ListActualWorkingTime
from annoworkcli.common.cli import (
    COMMAND_LINE_ERROR_STATUS_CODE,
    build_annoworkapi,
    get_list_from_args,
    prompt_yesnoall,
)

logger = logging.getLogger(__name__)


class DeleteActualWorkingTime:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
        organization_id: str,
        *,
        timezone_offset_hours: Optional[float],
        all_yes: bool,
    ):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

        self.list_actual_working_time_obj = ListActualWorkingTime(
            annowork_service=annowork_service,
            organization_id=organization_id,
            timezone_offset_hours=timezone_offset_hours,
        )

        self.all_yes = all_yes

    def delete_actual_working_times(self, actual_working_times: list[dict[str, Any]]):
        success_count = 0
        for index, actual in enumerate(actual_working_times):
            try:
                if not self.all_yes:
                    message = (
                        f"job_name={actual['job_name']}, user_id={actual['user_id']}, "
                        f"start_datetime={actual['start_datetime']}, end_datetime={actual['end_datetime']} のジョブを削除しますか？"
                        f" :: actual_working_time_id={actual['actual_working_time_id']}"
                    )
                    is_yes, all_yes = prompt_yesnoall(message)
                    if not is_yes:
                        continue
                    if all_yes:
                        self.all_yes = all_yes

                actual = self.annowork_service.api.delete_actual_working_time_by_organization_member(
                    self.organization_id,
                    organization_member_id=actual["organization_member_id"],
                    actual_working_time_id=actual["actual_working_time_id"],
                )
                logger.debug(f"{index+1} 件目: 実績作業時間を削除しました。:: {actual}")
                success_count += 1
            except Exception as e:
                logger.warning(f"{index+1} 件目: 実績作業時間の削除に失敗しました。{e}")
                continue
            finally:
                if (index + 1) % 100 == 0:
                    logger.debug(f"{index+1} 件 実績作業時間情報を削除しました。")

        logger.info(f"{success_count} / {len(actual_working_times)} 件の実績作業時間を削除しました。")

    def get_actual_working_times(
        self,
        *,
        start_date: str,
        end_date: str,
        job_id: Optional[str],
        user_id: Optional[str],
        actual_working_time_id_list: Optional[list[str]],
    ):
        get_actual_working_times = self.list_actual_working_time_obj.get_actual_working_times(
            user_ids=[user_id] if user_id is not None else None,
            job_ids=[job_id] if job_id is not None else None,
            start_date=start_date,
            end_date=end_date,
            is_set_additional_info=True,
        )

        if actual_working_time_id_list is not None:
            get_actual_working_times = [
                e for e in get_actual_working_times if e["actual_working_time_id"] in set(actual_working_time_id_list)
            ]

        return get_actual_working_times

    def main(
        self,
        *,
        job_id: Optional[str],
        user_id: Optional[str],
        start_date: str,
        end_date: str,
        actual_working_time_id_list: Optional[list[str]],
    ):
        actual_working_times = self.get_actual_working_times(
            start_date=start_date,
            end_date=end_date,
            job_id=job_id,
            user_id=user_id,
            actual_working_time_id_list=actual_working_time_id_list,
        )

        if len(actual_working_times) == 0:
            logger.info(f"削除する実績作業時間情報はありませんでした。")
            return

        message = (
            f"実績作業時間情報 {len(actual_working_times)} 件を削除します。よろしいですか？ :: "
            f"start_date={start_date}, end_date={end_date}, "
        )
        if job_id is not None:
            job = self.annowork_service.api.get_job(self.organization_id, job_id)
            message += f"job_id={job_id}, job_name={job['job_name']}, "
        if user_id is not None:
            message += f"user_id={user_id}, "

        if not self.all_yes:
            is_yes, all_yes = prompt_yesnoall(message)
            if not is_yes:
                return
            if all_yes:
                self.all_yes = all_yes

        self.delete_actual_working_times(actual_working_times)


def main(args):
    annowork_service = build_annoworkapi(args)

    if args.job_id is None and args.user_id is None:
        print("--job_id または --user_id を指定してください。", file=sys.stderr)
        sys.exit(COMMAND_LINE_ERROR_STATUS_CODE)

    actual_working_time_id_list = get_list_from_args(args.actual_working_time_id)
    DeleteActualWorkingTime(
        annowork_service=annowork_service,
        organization_id=args.organization_id,
        timezone_offset_hours=args.timezone_offset,
        all_yes=args.yes,
    ).main(
        job_id=args.job_id,
        user_id=args.user_id,
        actual_working_time_id_list=actual_working_time_id_list,
        start_date=args.start_date,
        end_date=args.end_date,
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    parser.add_argument("--start_date", type=str, required=True, help="削除したい実績作業時間情報の開始日(YYYY-mm-dd)を指定してください。")
    parser.add_argument("--end_date", type=str, required=True, help="削除したい実績作業時間情報の終了日(YYYY-mm-dd)を指定してください。")

    parser.add_argument("-j", "--job_id", type=str, required=False, help="削除したい実績作業時間情報に紐づくjob_idを指定してください。")
    parser.add_argument("-u", "--user_id", type=str, required=False, help="削除したい実績作業時間情報に紐づくuser_idを指定してください。")

    parser.add_argument(
        "--timezone_offset", type=float, help="日付に対するタイムゾーンのオフセット時間を指定します。例えばJSTなら '9' です。指定しない場合はローカルのタイムゾーンを参照します。"
    )

    parser.add_argument(
        "--actual_working_time_id",
        type=str,
        nargs="+",
        required=False,
        help="削除したい実績作業時間IDを指定してください。",
    )

    parser.add_argument("-y", "--yes", type=str, help="すべてのプロンプトに自動的に 'yes' と答えます。")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "delete"
    subcommand_help = "実績作業時間を削除します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
