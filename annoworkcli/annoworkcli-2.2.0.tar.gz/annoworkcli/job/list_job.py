from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Optional

import pandas
from annoworkapi.job import get_parent_job_id_from_job_tree
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import OutputFormat, build_annoworkapi, get_list_from_args
from annoworkcli.common.utils import print_csv, print_json

logger = logging.getLogger(__name__)


def filter_job_list_with_external_linkage_info_url(
    job_list: list[dict[str, Any]], external_linkage_info_url_list: list[str]
) -> list[dict[str, Any]]:
    result = []
    for job in job_list:
        url = job["external_linkage_info"].get("url")
        if url is None:
            continue
        url = url.strip()
        for target_url in external_linkage_info_url_list:
            target_url.strip()
            if url.startswith(target_url):
                result.append(job)
                break
    return result


class ListJob:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
        organization_id: str,
    ):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

    def get_job_list(
        self,
        *,
        job_id_list: Optional[list[str]] = None,
        parent_job_id_list: Optional[list[str]] = None,
        external_linkage_info_url_list: Optional[list[str]] = None,
        is_add_parent_job_info: bool = False,
    ) -> list[dict[str, Any]]:

        all_job_list = self.annowork_service.api.get_jobs(self.organization_id)
        job_list = all_job_list
        if job_id_list is not None:
            job_list = [job for job in job_list if job["job_id"] in set(job_id_list)]

        if parent_job_id_list is not None:
            job_list = [
                job for job in job_list if get_parent_job_id_from_job_tree(job["job_tree"]) in set(parent_job_id_list)
            ]

        if external_linkage_info_url_list is not None:
            job_list = filter_job_list_with_external_linkage_info_url(job_list, external_linkage_info_url_list)

        # 親のジョブ情報を追加する
        if is_add_parent_job_info:
            all_job_dict = {job["job_id"]: job for job in all_job_list}
            for job in job_list:
                parent_job_id = get_parent_job_id_from_job_tree(job["job_tree"])
                parent_job = all_job_dict.get(parent_job_id)
                if parent_job is not None:
                    job["parent_job_id"] = parent_job["job_id"]
                    job["parent_job_name"] = parent_job["job_name"]
                else:
                    job["parent_job_id"] = None
                    job["parent_job_name"] = None

        return job_list

    def main(
        self,
        output: Path,
        output_format: OutputFormat,
        *,
        job_id_list: Optional[list[str]],
        parent_job_id_list: Optional[list[str]],
        external_linkage_info_url_list: Optional[list[str]],
        is_add_parent_job_info: bool,
    ):
        job_list = self.get_job_list(
            job_id_list=job_id_list,
            parent_job_id_list=parent_job_id_list,
            external_linkage_info_url_list=external_linkage_info_url_list,
            is_add_parent_job_info=is_add_parent_job_info,
        )
        if len(job_list) == 0:
            logger.warning(f"ジョブ情報は0件なので、出力しません。")
            return

        logger.debug(f"{len(job_list)} 件のジョブ一覧を出力します。")

        if output_format == OutputFormat.JSON:
            print_json(job_list, is_pretty=True, output=output)
        else:
            df = pandas.json_normalize(job_list)
            print_csv(df, output=output)


def main(args):
    annowork_service = build_annoworkapi(args)

    job_id_list = get_list_from_args(args.job_id)
    parent_job_id_list = get_list_from_args(args.parent_job_id)
    external_linkage_info_url_list = get_list_from_args(args.external_linkage_info_url)

    ListJob(annowork_service=annowork_service, organization_id=args.organization_id).main(
        output=args.output,
        output_format=OutputFormat(args.format),
        job_id_list=job_id_list,
        parent_job_id_list=parent_job_id_list,
        external_linkage_info_url_list=external_linkage_info_url_list,
        is_add_parent_job_info=args.show_parent_job,
    )


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    job_id_group = parser.add_mutually_exclusive_group()
    job_id_group.add_argument(
        "-j",
        "--job_id",
        type=str,
        nargs="+",
        help="絞り込み対象であるジョブのjob_idを指定してください。",
    )

    job_id_group.add_argument(
        "-pj",
        "--parent_job_id",
        type=str,
        nargs="+",
        help="絞り込み対象である親のジョブのjob_idを指定してください。",
    )

    parser.add_argument(
        "--external_linkage_info_url",
        type=str,
        nargs="+",
        required=False,
        help="外部連携情報のURLで絞り込みます。URL末尾のスラッシュの有無に影響されないように、前方一致で絞り込みます。",
    )

    parser.add_argument(
        "--show_parent_job",
        action="store_true",
        help="親のジョブの情報も出力します。",
    )

    parser.add_argument("-o", "--output", type=Path, help="出力先")

    parser.add_argument(
        "-f", "--format", type=str, choices=[e.value for e in OutputFormat], help="出力先", default=OutputFormat.CSV.value
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "list"
    subcommand_help = "ジョブ一覧を出力します。"
    description = "ジョブ一覧を出力します。"

    parser = annoworkcli.common.cli.add_parser(subparsers, subcommand_name, subcommand_help, description)
    parse_args(parser)
    return parser
