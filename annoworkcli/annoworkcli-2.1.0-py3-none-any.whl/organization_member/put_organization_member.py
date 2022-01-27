from __future__ import annotations

import argparse
import logging
import uuid
from typing import Any, Collection, Optional

from annoworkapi.enums import Role
from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args

logger = logging.getLogger(__name__)


class PutOrganizationMember:
    def __init__(
        self,
        annowork_service: AnnoworkResource,
        organization_id: str,
    ):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

    def put_organization_member(
        self,
        user_id: str,
        role: str,
        organization_tag_id_list: Optional[Collection[str]],
        old_member: Optional[dict[str, Any]],
    ):
        """[summary]

        Args:
            user_id (str): [description]
            role (str): [description]
            organization_tag_id_list (Optional[list[str]]): [description]
            old_member (Optional[dict[str,Any]]): [description]
        """
        last_updated_datetime = None
        if old_member is not None:
            last_updated_datetime = old_member["updated_datetime"]
            organization_member_id = old_member["organization_member_id"]

        else:
            last_updated_datetime = None
            organization_member_id = str(uuid.uuid4())

        request_body: dict[str, Any] = {
            "user_id": user_id,
            "role": role,
            "organization_tags": organization_tag_id_list if organization_tag_id_list is not None else [],
        }
        if last_updated_datetime is not None:
            request_body["last_updated_datetime"] = last_updated_datetime

        logger.debug(f"{request_body=}")
        new_member = self.annowork_service.api.put_organization_member(
            self.organization_id, organization_member_id, request_body=request_body
        )
        logger.debug(f"{user_id=}, {organization_member_id=}: 組織メンバを追加しました。 :: {new_member}")
        return True

    def main(self, user_id_list: list[str], role: str, organization_tag_id_list: Optional[Collection[str]]):
        organization_members = self.annowork_service.api.get_organization_members(
            self.organization_id, query_params={"includes_inactive_members": True}
        )
        member_dict: dict[str, dict[str, Any]] = {m["user_id"]: m for m in organization_members}
        success_count = 0
        for user_id in user_id_list:
            try:
                result = self.put_organization_member(
                    user_id,
                    role,
                    organization_tag_id_list=organization_tag_id_list,
                    old_member=member_dict.get(user_id),
                )
                if result:
                    success_count += 1
            except Exception as e:
                logger.warning(f"{user_id=}: 組織メンバの登録に失敗しました。{e}")
                continue

        logger.info(f"{success_count}/{len(user_id_list)} 件のユーザを組織メンバに登録しました。")


def main(args):
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    organization_tag_id_list = get_list_from_args(args.organization_tag_id)
    assert user_id_list is not None
    PutOrganizationMember(
        annowork_service=annowork_service,
        organization_id=args.organization_id,
    ).main(user_id_list=user_id_list, role=args.role, organization_tag_id_list=organization_tag_id_list)


def parse_args(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-org",
        "--organization_id",
        type=str,
        required=True,
        help="対象の組織ID",
    )

    parser.add_argument(
        "-u",
        "--user_id",
        type=str,
        nargs="+",
        required=True,
        help="組織メンバに追加するuser_id",
    )

    parser.add_argument(
        "--role",
        type=str,
        choices=[e.value for e in Role],
        required=True,
        help="権限",
    )

    parser.add_argument(
        "-org_tag",
        "--organization_tag_id",
        type=str,
        nargs="+",
        required=False,
        help="メンバに付与する組織タグID",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "put"
    subcommand_help = "組織メンバを登録します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
