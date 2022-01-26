from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ...models import (
    GetGroupsAssociatedToChannelsByTeamResponse_200,
    GetGroupStatsResponse_200,
    GetGroupUsersResponse_200,
    Group,
    GroupSyncableChannel,
    GroupSyncableChannels,
    GroupSyncableTeam,
    GroupSyncableTeams,
    PatchGroupJsonBody,
    PatchGroupSyncableForChannelJsonBody,
    PatchGroupSyncableForTeamJsonBody,
    StatusOK,
)
from ..base import ApiBaseClass


class GroupsApi(ApiBaseClass):
    """Endpoints related to LDAP groups."""

    def unlink_ldap_group(
        self,
        remote_id: str,
    ) -> StatusOK:
        """Delete a link for LDAP group



        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/ldap/groups/{remote_id}/link".format(
            remote_id=remote_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def get_groups(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
        q: Optional[str] = None,
        include_member_count: Optional[bool] = None,
        not_associated_to_team: str,
        not_associated_to_channel: str,
        since: Optional[int] = None,
    ) -> List[Group]:
        """Get groups

        Retrieve a list of all groups not associated to a particular channel or
        team.

        `not_associated_to_team` **OR** `not_associated_to_channel` is required.

        If you use `not_associated_to_team`, you must be a team admin for that
        particular team (permission to manage that team).

        If you use `not_associated_to_channel`, you must be a channel admin for
        that particular channel (permission to manage that channel).

        Minimum Server Version:
            5.11
        """

        url = "/groups".format()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "q": q,
            "include_member_count": include_member_count,
            "not_associated_to_team": not_associated_to_team,
            "not_associated_to_channel": not_associated_to_channel,
            "since": since,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Group.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_group(
        self,
        group_id: str,
    ) -> Group:
        """Get a group

        Get group from the provided group id string

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}".format(
            group_id=group_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Group.parse_obj(response.json())

            return response_200
        return response

    def patch_group(
        self,
        group_id: str,
        *,
        json_body: PatchGroupJsonBody,
    ) -> Group:
        """Patch a group

        Partially update a group by providing only the fields you want to
        update. Omitted fields will not be updated. The fields that can be
        updated are defined in the request body, all other provided fields will
        be ignored.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/patch".format(
            group_id=group_id,
        )

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Group.parse_obj(response.json())

            return response_200
        return response

    def link_group_syncable_for_team(
        self,
        group_id: str,
        team_id: str,
    ) -> GroupSyncableTeam:
        """Link a team to a group

        Link a team to a group

        Permissions:
            Must have `manage_team` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/teams/{team_id}/link".format(
            group_id=group_id,
            team_id=team_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = GroupSyncableTeam.parse_obj(response.json())

            return response_201
        return response

    def unlink_group_syncable_for_team(
        self,
        group_id: str,
        team_id: str,
    ) -> StatusOK:
        """Delete a link from a team to a group

        Delete a link from a team to a group

        Permissions:
            Must have `manage_team` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/teams/{team_id}/link".format(
            group_id=group_id,
            team_id=team_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def link_group_syncable_for_channel(
        self,
        group_id: str,
        channel_id: str,
    ) -> GroupSyncableChannel:
        """Link a channel to a group

        Link a channel to a group
        Otherwise, you must have the `manage_public_channel_members` permission.

        Permissions:
            If the channel is private, you must have
        `manage_private_channel_members` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/channels/{channel_id}/link".format(
            group_id=group_id,
            channel_id=channel_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = GroupSyncableChannel.parse_obj(response.json())

            return response_201
        return response

    def unlink_group_syncable_for_channel(
        self,
        group_id: str,
        channel_id: str,
    ) -> StatusOK:
        """Delete a link from a channel to a group

        Delete a link from a channel to a group
        Otherwise, you must have the `manage_public_channel_members` permission.

        Permissions:
            If the channel is private, you must have
        `manage_private_channel_members` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/channels/{channel_id}/link".format(
            group_id=group_id,
            channel_id=channel_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def get_group_syncable_for_team_id(
        self,
        group_id: str,
        team_id: str,
    ) -> GroupSyncableTeam:
        """Get GroupSyncable from Team ID

        Get the GroupSyncable object with group_id and team_id from params

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/teams/{team_id}".format(
            group_id=group_id,
            team_id=team_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GroupSyncableTeam.parse_obj(response.json())

            return response_200
        return response

    def get_group_syncable_for_channel_id(
        self,
        group_id: str,
        channel_id: str,
    ) -> GroupSyncableChannel:
        """Get GroupSyncable from channel ID

        Get the GroupSyncable object with group_id and channel_id from params

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/channels/{channel_id}".format(
            group_id=group_id,
            channel_id=channel_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GroupSyncableChannel.parse_obj(response.json())

            return response_200
        return response

    def get_group_syncables_teams(
        self,
        group_id: str,
    ) -> List[GroupSyncableTeams]:
        """Get group teams

        Retrieve the list of teams associated to the group

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/teams".format(
            group_id=group_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = GroupSyncableTeams.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_group_syncables_channels(
        self,
        group_id: str,
    ) -> List[GroupSyncableChannels]:
        """Get group channels

        Retrieve the list of channels associated to the group

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/channels".format(
            group_id=group_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = GroupSyncableChannels.parse_obj(
                    response_200_item_data
                )

                response_200.append(response_200_item)

            return response_200
        return response

    def patch_group_syncable_for_team(
        self,
        group_id: str,
        team_id: str,
        *,
        json_body: PatchGroupSyncableForTeamJsonBody,
    ) -> GroupSyncableTeam:
        """Patch a GroupSyncable associated to Team

        Partially update a GroupSyncable by providing only the fields you want
        to update. Omitted fields will not be updated. The fields that can be
        updated are defined in the request body, all other provided fields will
        be ignored.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/teams/{team_id}/patch".format(
            group_id=group_id,
            team_id=team_id,
        )

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GroupSyncableTeam.parse_obj(response.json())

            return response_200
        return response

    def patch_group_syncable_for_channel(
        self,
        group_id: str,
        channel_id: str,
        *,
        json_body: PatchGroupSyncableForChannelJsonBody,
    ) -> GroupSyncableChannel:
        """Patch a GroupSyncable associated to Channel

        Partially update a GroupSyncable by providing only the fields you want
        to update. Omitted fields will not be updated. The fields that can be
        updated are defined in the request body, all other provided fields will
        be ignored.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/channels/{channel_id}/patch".format(
            group_id=group_id,
            channel_id=channel_id,
        )

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GroupSyncableChannel.parse_obj(response.json())

            return response_200
        return response

    def get_group_users(
        self,
        group_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> GetGroupUsersResponse_200:
        """Get group users

        Retrieve the list of users associated with a given group.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/groups/{group_id}/members".format(
            group_id=group_id,
        )
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GetGroupUsersResponse_200.parse_obj(response.json())

            return response_200
        return response

    def get_group_stats(
        self,
        group_id: str,
    ) -> GetGroupStatsResponse_200:
        """Get group stats

        Retrieve the stats of a given group.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.26
        """

        url = "/groups/{group_id}/stats".format(
            group_id=group_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GetGroupStatsResponse_200.parse_obj(response.json())

            return response_200
        return response

    def get_groups_by_channel(
        self,
        channel_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
        filter_allow_reference: Optional[bool] = False,
    ) -> List[Group]:
        """Get channel groups

        Retrieve the list of groups associated with a given channel.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.11
        """

        url = "/channels/{channel_id}/groups".format(
            channel_id=channel_id,
        )
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "filter_allow_reference": filter_allow_reference,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Group.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_groups_by_team(
        self,
        team_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
        filter_allow_reference: Optional[bool] = False,
    ) -> List[Group]:
        """Get team groups

        Retrieve the list of groups associated with a given team.

        Minimum Server Version:
            5.11
        """

        url = "/teams/{team_id}/groups".format(
            team_id=team_id,
        )
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "filter_allow_reference": filter_allow_reference,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Group.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_groups_associated_to_channels_by_team(
        self,
        team_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
        filter_allow_reference: Optional[bool] = False,
    ) -> GetGroupsAssociatedToChannelsByTeamResponse_200:
        """Get team groups by channels

        Retrieve the set of groups associated with the channels in the given
        team grouped by channel.

        Permissions:
            Must have `manage_system` permission or can access only for current
        user
        Minimum Server Version:
            5.11
        """

        url = "/teams/{team_id}/groups_by_channels".format(
            team_id=team_id,
        )
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "filter_allow_reference": filter_allow_reference,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GetGroupsAssociatedToChannelsByTeamResponse_200.parse_obj(
                response.json()
            )

            return response_200
        return response

    def get_groups_by_user_id(
        self,
        user_id: str,
    ) -> List[Group]:
        """Get groups for a userId

        Retrieve the list of groups associated to the user

        Minimum Server Version:
            5.24
        """

        url = "/users/{user_id}/groups".format(
            user_id=user_id,
        )

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Group.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response
