from typing import Optional

import jwt

from pyteamtv.infra.requester import Requester
from pyteamtv.models.list import List
from pyteamtv.models.membership import Membership
from pyteamtv.models.membership_list import MembershipList
from pyteamtv.models.sharing_group import SharingGroup

from .endpoint import API_ENDPOINT
from .token import TOKEN
from ..exceptions import TeamNotFound, InputError
from ..models.resource_group.team import TeamResourceGroup


class TeamTVUser(object):
    def __init__(self, jwt_token):
        self.jwt_token = jwt_token

        token = jwt.decode(
            jwt_token,
            TOKEN,
            algorithms='RS256',
            verify=False,
            options={
                'verify_signature': False
            }
        )

        self._requester = Requester(
            f"{API_ENDPOINT}/api",
            jwt_token
        )
        self.__token = token

    def get_membership_list(self):
        """
        :return: MembershipList
        """
        return MembershipList(
            Membership,
            self._requester,
            "GET",
            "/users/me/memberships"
        )

    def get_public_sharing_groups(self):
        return List(
            SharingGroup,
            self._requester,
            "GET",
            "/sharingGroups"
        )

    def get_team(self, name: Optional[str] = None, resource_group_id: Optional[str] = None) -> TeamResourceGroup:
        membership_list = self.get_membership_list()
        if resource_group_id:
            membership = membership_list.get_membership_by_resource_group_id(
                resource_group_id
            )
        elif name:
            membership = membership_list.get_membership_by_name(
                name=name
            )
        else:
            raise InputError(f"Either `name` or `resource_group_id` must be specified.")

        if not membership:
            raise TeamNotFound(f"No team named '{name}' found.")
        return membership.resource_group


