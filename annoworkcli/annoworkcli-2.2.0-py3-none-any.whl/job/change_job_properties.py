from __future__ import annotations

import argparse
import logging
from typing import Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args, prompt_yesnoall

logger = logging.getLogger(__name__)


class ChangeJobProperties:
    def __init__(self, annowork_service: AnnoworkResource, organization_id: str, *, all_yes: bool):
        self.annowork_service = annowork_service
        self.organization_id = organization_id
        self.all_yes = all_yes

    def change_job_status(self, job_id: str, status: str) -> bool:
        job = self.annowork_service.wrapper.get_job_or_none(self.organization_id, job_id)
        if job is None:
            logger.warning(f"{job_id=} のジョブは存在しませんでした。")
            return False

        if not self.all_yes:
            is_yes, all_yes = prompt_yesnoall(
                f"job_id={job_id}, job_name={job['job_name']}" f" のジョブのステータスを '{status}' に変更しますか？"
            )
            if not is_yes:
                return False
            if all_yes:
                self.all_yes = all_yes

        request_body = {"job_name": job["job_name"], "status": status, "last_updated_datetime": job["updated_datetime"]}
        if job["note"] is not None:
            request_body["note"] = job["note"]
        if job["target_hours"] is not None:
            request_body["target_hours"] = job["target_hours"]
        if job["external_linkage_info"] is not None:
            request_body["external_linkage_info"] = job["external_linkage_info"]

        new_job = self.annowork_service.api.put_job(self.organization_id, job_id, request_body=request_body)
        logger.debug(f"ジョブのステータスを変更しました。 :: {new_job}")
        return True

    def main(self, *, job_id_list: list[str], status: str):
        logger.info(f"{len(job_id_list)} 件のジョブのステータスを変更します。")
        success_count = 0
        for job_id in job_id_list:
            try:
                result = self.change_job_status(job_id, status=status)
                if result:
                    success_count += 1
            except Exception as e:
                logger.warning(f"{job_id=} のジョブのステータスの変更に失敗しました。{e}")

        logger.info(f"{success_count} / {len(job_id_list)} 件のジョブのステータスを変更しました。")


def main(args):
    annowork_service = build_annoworkapi(args)
    job_id_list = get_list_from_args(args.job_id)
    assert job_id_list is not None

    ChangeJobProperties(annowork_service=annowork_service, organization_id=args.organization_id, all_yes=args.yes).main(
        job_id_list=job_id_list, status=args.status
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    parser.add_argument(
        "-j",
        "--job_id",
        type=str,
        nargs="+",
        required=True,
        help="ステータスを変更するジョブのjob_idを指定してください。",
    )

    parser.add_argument(
        "--status",
        type=str,
        required=True,
        choices=["archived", "unarchived"],
        help="変更後のステータスを指定してください。",
    )

    parser.add_argument("-y", "--yes", type=str, help="すべてのプロンプトに自動的に 'yes' と答えます。")

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "change"
    subcommand_help = "ジョブの情報（ステータスなど）を変更します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
