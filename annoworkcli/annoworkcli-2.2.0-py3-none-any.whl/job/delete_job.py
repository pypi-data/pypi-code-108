from __future__ import annotations

import argparse
import logging
from typing import Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, prompt_yesnoall

logger = logging.getLogger(__name__)


class DeleteJob:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str, *, all_yes: bool):
        self.annowork_service = annowork_service
        self.organization_id = organization_id
        self.all_yes = all_yes

    def delete_job(self, job_id: str) -> bool:
        job = self.annowork_service.wrapper.get_job_or_none(self.organization_id, job_id)
        if job is None:
            logger.warning(f"{job_id=} のジョブは存在しませんでした。")
            return False

        if job["status"] != "archived":
            logger.warning(f"ジョブのstatusが 'archived' でないので、ジョブの削除をスキップします。 :: {job}")
            return False

        if not self.all_yes:
            is_yes, all_yes = prompt_yesnoall(f"job_id={job_id}, job_name={job['job_name']} のジョブを削除しますか？")
            if not is_yes:
                return False
            if all_yes:
                self.all_yes = all_yes

        self.annowork_service.api.delete_job(self.organization_id, job_id)
        logger.debug(f"ジョブを削除しました。 :: {job}")
        return True

    def main(
        self,
        job_id_list: list[str],
    ):
        logger.info(f"{len(job_id_list)} 件のジョブを削除します。")
        success_count = 0
        for job_id in job_id_list:
            try:
                result = self.delete_job(job_id)
                if result:
                    success_count += 1
            except Exception as e:
                logger.warning(f"{job_id=} のジョブの削除に失敗しました。{e}", e)
        logger.info(f"{success_count} / {len(job_id_list)} 件のジョブを削除しました。")


def main(args):
    annowork_service = build_annoworkapi(args)
    job_id_list = [args.job_id]

    DeleteJob(annowork_service=annowork_service, organization_id=args.organization_id, all_yes=args.yes).main(
        job_id_list,
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    # 間違えてたくさんのジョブを削除してしまわないようにするため、1つのjob_idしか指定できないようにする
    parser.add_argument(
        "-j",
        "--job_id",
        type=str,
        required=True,
        help="削除するジョブのjob_idを指定してください。",
    )

    parser.add_argument("-y", "--yes", type=str, help="すべてのプロンプトに自動的に 'yes' と答えます。")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "delete"
    subcommand_help = "ジョブを削除します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
