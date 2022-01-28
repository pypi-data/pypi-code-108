from __future__ import annotations

import argparse
import logging
from typing import Optional

from annofabapi import build as build_annofabapi
from annofabapi.resource import Resource as AnnofabResource
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi

logger = logging.getLogger(__name__)


class PutJobFromAnnofabProject:
    def __init__(
        self,
        *,
        annowork_service: AnnoworkResource,
        organization_id: str,
        annofab_service: AnnofabResource,
    ):
        self.annowork_service = annowork_service
        self.organization_id = organization_id
        self.annofab_service = annofab_service

    def put_job_from_annofab_project(
        self, parent_job_id: str, annofab_project_id: str, job_id: Optional[str] = None
    ) -> bool:
        af_project = self.annofab_service.wrapper.get_project_or_none(annofab_project_id)
        if af_project is None:
            logger.warning(f"{annofab_project_id=} にアクセスできません。ジョブの登録処理をスキップします。")
            return False

        new_job_id = job_id if job_id is not None else annofab_project_id

        old_job = self.annowork_service.wrapper.get_job_or_none(self.organization_id, new_job_id)
        if old_job is not None:
            logger.warning(f"job_id='{new_job_id}' は既に存在します。ジョブの登録処理をスキップします。")
            return False

        annofab_project_url = f"https://annofab.com/projects/{annofab_project_id}"
        request_body = {
            "job_name": af_project["title"],
            "status": "unarchived",
            "parent_job_id": parent_job_id,
            "external_linkage_info": {"url": annofab_project_url},
        }

        new_job = self.annowork_service.api.put_job(self.organization_id, new_job_id, request_body=request_body)
        logger.debug(f"annofab_project_id={annofab_project_id} に対応するジョブを作成しました。 :: {new_job}")
        return True


def main(args):
    annowork_service = build_annoworkapi(args)
    main_obj = PutJobFromAnnofabProject(
        annowork_service=annowork_service, organization_id=args.organization_id, annofab_service=build_annofabapi()
    )
    main_obj.put_job_from_annofab_project(
        parent_job_id=args.parent_job_id, annofab_project_id=args.annofab_project_id, job_id=args.job_id
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
        "-pj",
        "--parent_job_id",
        type=str,
        required=True,
        help="追加するジョブが所属する親ジョブのjob_idを指定してください。",
    )

    parser.add_argument(
        "-af_p",
        "--annofab_project_id",
        type=str,
        required=True,
        help="追加するジョブに紐付けるAnnofabプロジェクトのproject_idを指定してください。",
    )

    parser.add_argument(
        "-j",
        "--job_id",
        type=str,
        required=False,
        help="追加するジョブのjob_idを指定してください。未指定の場合は ``--annofab_project_id`` の値と同じです。",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "put_job"
    subcommand_help = "Annofabプロジェクトからジョブを作成します。"
    description = "Annofabプロジェクトからジョブを作成します。\n" "job_idは指定したannofab_project_idと同じ値にします。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description=description)
    parse_args(parser)
    return parser
