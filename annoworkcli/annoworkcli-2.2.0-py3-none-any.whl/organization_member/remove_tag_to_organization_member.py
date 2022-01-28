from __future__ import annotations

import argparse
import logging
from typing import Any, Collection, Optional

from annoworkapi.resource import Resource as AnnoworkResource

import annoworkcli
from annoworkcli.common.cli import build_annoworkapi, get_list_from_args

logger = logging.getLogger(__name__)


class RemoveTagToOrganizationMember:
    def __init__(
        self,
        *,
        annowork_service: AnnoworkResource,
        organization_id: str,
    ):
        self.annowork_service = annowork_service
        self.organization_id = organization_id

    def put_organization_member(
        self,
        user_id: str,
        *,
        old_organization_tag_ids: Collection[str],
        organization_tag_ids: Collection[str],
        old_member: dict[str, Any],
    ) -> bool:
        organization_member_id = old_member["organization_member_id"]

        new_organization_tags = list(set(old_organization_tag_ids) - set(organization_tag_ids))
        request_body: dict[str, Any] = {
            "user_id": user_id,
            "role": old_member["role"],
            "organization_tags": new_organization_tags,
            "last_updated_datetime": old_member["updated_datetime"],
        }

        new_member = self.annowork_service.api.put_organization_member(
            self.organization_id, organization_member_id, request_body=request_body
        )
        logger.debug(f"{user_id=}, {organization_member_id=}: 組織メンバから組織タグを削除しました。 :: {new_member}")
        return True

    def main(self, user_id_list: list[str], organization_tag_ids: Collection[str]):
        organization_members = self.annowork_service.api.get_organization_members(
            self.organization_id, query_params={"includes_inactive_members": True}
        )
        member_dict: dict[str, dict[str, Any]] = {m["user_id"]: m for m in organization_members}
        success_count = 0
        for user_id in user_id_list:
            try:
                old_member = member_dict.get(user_id)
                if old_member is None:
                    logger.warning(f"{user_id=} のユーザは組織メンバに存在しないので、スキップします。")
                    continue

                old_tags = self.annowork_service.api.get_organization_member_tags(
                    self.organization_id, old_member["organization_member_id"]
                )
                old_organization_tag_ids = {e["organization_tag_id"] for e in old_tags}
                diff_tags = old_organization_tag_ids - set(organization_tag_ids)
                if old_organization_tag_ids == diff_tags:
                    logger.warning(f"{user_id=} には、すでに組織タグ {organization_tag_ids} が設定されていないので、スキップします。")
                    continue

                result = self.put_organization_member(
                    user_id,
                    old_organization_tag_ids=old_organization_tag_ids,
                    organization_tag_ids=organization_tag_ids,
                    old_member=old_member,
                )
                if result:
                    success_count += 1
            except Exception as e:
                logger.warning(f"{user_id=}: 組織タグの削除に失敗しました。{e}", e)
                continue

        logger.info(f"{success_count}/{len(user_id_list)} 件のユーザから組織タグを削除しました。")


def main(args):
    annowork_service = build_annoworkapi(args)
    user_id_list = get_list_from_args(args.user_id)
    organization_tag_id_list = get_list_from_args(args.organization_tag_id)
    assert user_id_list is not None
    assert organization_tag_id_list is not None

    RemoveTagToOrganizationMember(
        annowork_service=annowork_service,
        organization_id=args.organization_id,
    ).main(user_id_list=user_id_list, organization_tag_ids=organization_tag_id_list)


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
        help="対象ユーザのuser_id",
    )

    parser.add_argument(
        "-org_tag",
        "--organization_tag_id",
        type=str,
        nargs="+",
        required=True,
        help="メンバから削除する組織タグID",
    )

    parser.set_defaults(subcommand_func=main)


def add_parser(subparsers: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:
    subcommand_name = "remove_tag"
    subcommand_help = "組織メンバから組織タグを削除します。"

    parser = annoworkcli.common.cli.add_parser(
        subparsers, subcommand_name, subcommand_help, description=subcommand_help
    )
    parse_args(parser)
    return parser
