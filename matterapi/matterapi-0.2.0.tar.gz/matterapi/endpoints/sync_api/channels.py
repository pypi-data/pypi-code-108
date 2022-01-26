from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel

from ...models import (
    AddChannelMemberJsonBody,
    Channel,
    ChannelListWithTeamData,
    ChannelMember,
    ChannelModeration,
    ChannelModerationPatch,
    ChannelNotifyProps,
    ChannelStats,
    ChannelUnread,
    CreateChannelJsonBody,
    MoveChannelJsonBody,
    OrderedSidebarCategories,
    PatchChannelJsonBody,
    PostList,
    SearchArchivedChannelsJsonBody,
    SearchChannelsJsonBody,
    SearchGroupChannelsJsonBody,
    SidebarCategory,
    StatusOK,
    UpdateChannelJsonBody,
    UpdateChannelMemberSchemeRolesJsonBody,
    UpdateChannelPrivacyJsonBody,
    UpdateChannelRolesJsonBody,
    UpdateChannelSchemeJsonBody,
    ViewChannelJsonBody,
    ViewChannelResponse_200,
)
from ..base import ApiBaseClass


class ChannelsApi(ApiBaseClass):
    """Endpoints for creating, getting and interacting with channels."""

    def get_all_channels(
        self,
        *,
        not_associated_to_group: Optional[str] = None,
        page: Optional[int] = 0,
        per_page: Optional[int] = 0,
        exclude_default_channels: Optional[bool] = False,
        exclude_policy_constrained: Optional[bool] = False,
    ) -> ChannelListWithTeamData:
        """Get a list of all channels



        Permissions:
            `manage_system`
        """

        url = "/channels".format()
        params: Dict[str, Any] = {
            "not_associated_to_group": not_associated_to_group,
            "page": page,
            "per_page": per_page,
            "exclude_default_channels": exclude_default_channels,
            "exclude_policy_constrained": exclude_policy_constrained,
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
            response_200 = ChannelListWithTeamData.parse_obj(response.json())

            return response_200
        return response

    def create_channel(
        self,
        *,
        json_body: CreateChannelJsonBody,
    ) -> Channel:
        """Create a channel

        Create a new channel.

        Permissions:
            If creating a public channel, `create_public_channel` permission is
        required. If creating a private channel, `create_private_channel`
        permission is required.
        """

        url = "/channels".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = Channel.parse_obj(response.json())

            return response_201
        return response

    def create_direct_channel(
        self,
        *,
        json_body: List[str],
    ) -> Channel:
        """Create a direct message channel

        Create a new direct message channel between two users.

        Permissions:
            Must be one of the two users and have `create_direct_channel`
        permission. Having the `manage_system` permission voids the previous
        requirements.
        """

        url = "/channels/direct".format()
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = Channel.parse_obj(response.json())

            return response_201
        return response

    def create_group_channel(
        self,
        *,
        json_body: List[str],
    ) -> Channel:
        """Create a group message channel

        Create a new group message channel to group of users. If the logged in
        user's id is not included in the list, it will be appended to the end.

        Permissions:
            Must have `create_group_channel` permission.
        """

        url = "/channels/group".format()
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = Channel.parse_obj(response.json())

            return response_201
        return response

    def search_group_channels(
        self,
        *,
        json_body: SearchGroupChannelsJsonBody,
    ) -> List[Channel]:
        """Search Group Channels

        Get a list of group channels for a user which members' usernames match
        the search term.

        Minimum Server Version:
            5.14
        """

        url = "/channels/group/search".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Channel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_public_channels_by_ids_for_team(
        self,
        team_id: str,
        *,
        json_body: List[str],
    ) -> List[Channel]:
        """Get a list of channels by ids

        Get a list of public channels on a team by id.

        Permissions:
            `view_team` for the team the channels are on.
        """

        url = "/teams/{team_id}/channels/ids".format(
            team_id=team_id,
        )
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Channel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_channel_members_timezones(
        self,
        channel_id: str,
    ) -> List[str]:
        """Get timezones in a channel

        Get a list of timezones for the users who are in this channel.

        Permissions:
            Must have the `read_channel` permission.
        Minimum Server Version:
            5.6
        """

        url = "/channels/{channel_id}/timezones".format(
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
            response_200 = cast(List[str], response.json())

            return response_200
        return response

    def get_channel(
        self,
        channel_id: str,
    ) -> Channel:
        """Get a channel

        Get channel from the provided channel id string.

        Permissions:
            `read_channel` permission for the channel.
        """

        url = "/channels/{channel_id}".format(
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
            response_200 = Channel.parse_obj(response.json())

            return response_200
        return response

    def update_channel(
        self,
        channel_id: str,
        *,
        json_body: UpdateChannelJsonBody,
    ) -> Channel:
        """Update a channel

        Update a channel. The fields that can be updated are listed as
        parameters. Omitted fields will be treated as blanks.

        Permissions:
            If updating a public channel, `manage_public_channel_members`
        permission is required. If updating a private channel,
        `manage_private_channel_members` permission is required.
        """

        url = "/channels/{channel_id}".format(
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
            response_200 = Channel.parse_obj(response.json())

            return response_200
        return response

    def delete_channel(
        self,
        channel_id: str,
    ) -> StatusOK:
        """Delete a channel

        Soft deletes a channel, by marking the channel as deleted in the
        database. Soft deleted channels will not be accessible in the user
        interface. Direct and group message channels cannot be deleted.

        As of server version 5.28, optionally use the `permanent=true` query
        parameter to permanently delete the channel for compliance reasons. To
        use this feature `ServiceSettings.EnableAPIChannelDeletion` must be set
        to `true` in the server's configuration.

        `delete_private_channel` permission if the channel is private,
        or have `manage_system` permission.

        Permissions:
            `delete_public_channel` permission if the channel is public,
        """

        url = "/channels/{channel_id}".format(
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

    def patch_channel(
        self,
        channel_id: str,
        *,
        json_body: PatchChannelJsonBody,
    ) -> Channel:
        """Patch a channel

        Partially update a channel by providing only the fields you want to
        update. Omitted fields will not be updated. The fields that can be
        updated are defined in the request body, all other provided fields will
        be ignored.

        Permissions:
            If updating a public channel, `manage_public_channel_members`
        permission is required. If updating a private channel,
        `manage_private_channel_members` permission is required.
        """

        url = "/channels/{channel_id}/patch".format(
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
            response_200 = Channel.parse_obj(response.json())

            return response_200
        return response

    def update_channel_privacy(
        self,
        channel_id: str,
        *,
        json_body: UpdateChannelPrivacyJsonBody,
    ) -> Channel:
        """Update channel's privacy

        Updates channel's privacy allowing changing a channel from Public to
        Private and back.

        Permissions:
            `manage_team` permission for the channels team on version < 5.28.
        `convert_public_channel_to_private` permission for the channel if
        updating privacy to 'P' on version >= 5.28.
        `convert_private_channel_to_public` permission for the channel if
        updating privacy to 'O' on version >= 5.28.
        Minimum Server Version:
            5.16
        """

        url = "/channels/{channel_id}/privacy".format(
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
            response_200 = Channel.parse_obj(response.json())

            return response_200
        return response

    def restore_channel(
        self,
        channel_id: str,
    ) -> Channel:
        """Restore a channel

        Restore channel from the provided channel id string.

        Permissions:
            `manage_team` permission for the team of the channel.
        Minimum Server Version:
            3.10
        """

        url = "/channels/{channel_id}/restore".format(
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

        if response.status_code == 200:
            response_200 = Channel.parse_obj(response.json())

            return response_200
        return response

    def move_channel(
        self,
        channel_id: str,
        *,
        json_body: MoveChannelJsonBody,
    ) -> Channel:
        """Move a channel

        Move a channel to another team.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.26
        """

        url = "/channels/{channel_id}/move".format(
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
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Channel.parse_obj(response.json())

            return response_200
        return response

    def get_channel_stats(
        self,
        channel_id: str,
    ) -> ChannelStats:
        """Get channel statistics

        Get statistics for a channel.

        Permissions:
            Must have the `read_channel` permission.
        """

        url = "/channels/{channel_id}/stats".format(
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
            response_200 = ChannelStats.parse_obj(response.json())

            return response_200
        return response

    def get_pinned_posts(
        self,
        channel_id: str,
    ) -> PostList:
        """Get a channel's pinned posts

        Get a list of pinned posts for channel.
        """

        url = "/channels/{channel_id}/pinned".format(
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
            response_200 = PostList.parse_obj(response.json())

            return response_200
        return response

    def get_public_channels_for_team(
        self,
        team_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[Channel]:
        """Get public channels

        Get a page of public channels on a team based on query string parameters
        - page and per_page.

        Permissions:
            Must be authenticated and have the `list_team_channels` permission.
        """

        url = "/teams/{team_id}/channels".format(
            team_id=team_id,
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Channel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_private_channels_for_team(
        self,
        team_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[Channel]:
        """Get private channels

        Get a page of private channels on a team based on query string
        parameters - team_id, page and per_page.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.26
        """

        url = "/teams/{team_id}/channels/private".format(
            team_id=team_id,
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Channel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_deleted_channels_for_team(
        self,
        team_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[Channel]:
        """Get deleted channels

        Get a page of deleted channels on a team based on query string
        parameters - team_id, page and per_page.

        Minimum Server Version:
            3.10
        """

        url = "/teams/{team_id}/channels/deleted".format(
            team_id=team_id,
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Channel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def autocomplete_channels_for_team(
        self,
        team_id: str,
        *,
        name: str,
    ) -> List[Channel]:
        """Autocomplete channels

        Autocomplete public channels on a team based on the search term provided
        in the request URL.

        Permissions:
            Must have the `list_team_channels` permission.
        Minimum Server Version:
            4.7
        """

        url = "/teams/{team_id}/channels/autocomplete".format(
            team_id=team_id,
        )
        params: Dict[str, Any] = {
            "name": name,
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
                response_200_item = Channel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def autocomplete_channels_for_team_for_search(
        self,
        team_id: str,
        *,
        name: str,
    ) -> List[Channel]:
        """Autocomplete channels for search

        Autocomplete your channels on a team based on the search term provided
        in the request URL.

        Permissions:
            Must have the `list_team_channels` permission.
        Minimum Server Version:
            5.4
        """

        url = "/teams/{team_id}/channels/search_autocomplete".format(
            team_id=team_id,
        )
        params: Dict[str, Any] = {
            "name": name,
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
                response_200_item = Channel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def search_channels(
        self,
        team_id: str,
        *,
        json_body: SearchChannelsJsonBody,
    ) -> List[Channel]:
        """Search channels

        Search public channels on a team based on the search term provided in
        the request body.

        In server version 5.16 and later, a user without the
        `list_team_channels` permission will be able to use this endpoint, with
        the search results limited to the channels that the user is a member of.

        Permissions:
            Must have the `list_team_channels` permission.
        """

        url = "/teams/{team_id}/channels/search".format(
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
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = []
            _response_201 = response.json()
            for response_201_item_data in _response_201:
                response_201_item = Channel.parse_obj(response_201_item_data)

                response_201.append(response_201_item)

            return response_201
        return response

    def search_archived_channels(
        self,
        team_id: str,
        *,
        json_body: SearchArchivedChannelsJsonBody,
    ) -> List[Channel]:
        """Search archived channels

        Search archived channels on a team based on the search term provided in
        the request body.

        In server version 5.18 and later, a user without the
        `list_team_channels` permission will be able to use this endpoint, with
        the search results limited to the channels that the user is a member of.

        Permissions:
            Must have the `list_team_channels` permission.
        Minimum Server Version:
            5.18
        """

        url = "/teams/{team_id}/channels/search_archived".format(
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
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = []
            _response_201 = response.json()
            for response_201_item_data in _response_201:
                response_201_item = Channel.parse_obj(response_201_item_data)

                response_201.append(response_201_item)

            return response_201
        return response

    def get_channel_by_name(
        self,
        team_id: str,
        channel_name: str,
        *,
        include_deleted: Optional[bool] = False,
    ) -> Channel:
        """Get a channel by name

        Gets channel from the provided team id and channel name strings.

        Permissions:
            `read_channel` permission for the channel.
        """

        url = "/teams/{team_id}/channels/name/{channel_name}".format(
            team_id=team_id,
            channel_name=channel_name,
        )
        params: Dict[str, Any] = {
            "include_deleted": include_deleted,
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
            response_200 = Channel.parse_obj(response.json())

            return response_200
        return response

    def get_channel_by_name_for_team_name(
        self,
        team_name: str,
        channel_name: str,
        *,
        include_deleted: Optional[bool] = False,
    ) -> Channel:
        """Get a channel by name and team name

        Gets a channel from the provided team name and channel name strings.

        Permissions:
            `read_channel` permission for the channel.
        """

        url = "/teams/name/{team_name}/channels/name/{channel_name}".format(
            team_name=team_name,
            channel_name=channel_name,
        )
        params: Dict[str, Any] = {
            "include_deleted": include_deleted,
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
            response_200 = Channel.parse_obj(response.json())

            return response_200
        return response

    def get_channel_members(
        self,
        channel_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[ChannelMember]:
        """Get channel members

        Get a page of members for a channel.

        Permissions:
            `read_channel` permission for the channel.
        """

        url = "/channels/{channel_id}/members".format(
            channel_id=channel_id,
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = ChannelMember.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def add_channel_member(
        self,
        channel_id: str,
        *,
        json_body: AddChannelMemberJsonBody,
    ) -> ChannelMember:
        """Add user to channel

        Add a user to a channel by creating a channel member object.
        """

        url = "/channels/{channel_id}/members".format(
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
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = ChannelMember.parse_obj(response.json())

            return response_201
        return response

    def get_channel_members_by_ids(
        self,
        channel_id: str,
        *,
        json_body: List[str],
    ) -> List[ChannelMember]:
        """Get channel members by ids

        Get a list of channel members based on the provided user ids.

        Permissions:
            Must have the `read_channel` permission.
        """

        url = "/channels/{channel_id}/members/ids".format(
            channel_id=channel_id,
        )
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = ChannelMember.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_channel_member(
        self,
        channel_id: str,
        user_id: str,
    ) -> ChannelMember:
        """Get channel member

        Get a channel member.

        Permissions:
            `read_channel` permission for the channel.
        """

        url = "/channels/{channel_id}/members/{user_id}".format(
            channel_id=channel_id,
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
            response_200 = ChannelMember.parse_obj(response.json())

            return response_200
        return response

    def remove_user_from_channel(
        self,
        channel_id: str,
        user_id: str,
    ) -> StatusOK:
        """Remove user from channel

        Delete a channel member, effectively removing them from a channel.

        In server version 5.3 and later, channel members can only be deleted
        from public or private channels.
        `manage_private_channel_members` permission if the channel is private.

        Permissions:
            `manage_public_channel_members` permission if the channel is public.
        """

        url = "/channels/{channel_id}/members/{user_id}".format(
            channel_id=channel_id,
            user_id=user_id,
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

    def update_channel_roles(
        self,
        channel_id: str,
        user_id: str,
        *,
        json_body: UpdateChannelRolesJsonBody,
    ) -> StatusOK:
        """Update channel roles

        Update a user's roles for a channel.

        Permissions:
            Must have `manage_channel_roles` permission for the channel.
        """

        url = "/channels/{channel_id}/members/{user_id}/roles".format(
            channel_id=channel_id,
            user_id=user_id,
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def update_channel_member_scheme_roles(
        self,
        channel_id: str,
        user_id: str,
        *,
        json_body: UpdateChannelMemberSchemeRolesJsonBody,
    ) -> StatusOK:
        """Update the scheme-derived roles of a channel member.

        Update a channel member's scheme_admin/scheme_user properties. Typically
        this should either be `scheme_admin=false, scheme_user=true` for
        ordinary channel member, or `scheme_admin=true, scheme_user=true` for a
        channel admin.

        Permissions:
            Must be authenticated and have the `manage_channel_roles`
        permission.
        Minimum Server Version:
            5.0
        """

        url = "/channels/{channel_id}/members/{user_id}/schemeRoles".format(
            channel_id=channel_id,
            user_id=user_id,
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def update_channel_notify_props(
        self,
        channel_id: str,
        user_id: str,
        *,
        json_body: ChannelNotifyProps,
    ) -> StatusOK:
        """Update channel notifications

        Update a user's notification properties for a channel. Only the provided
        fields are updated.

        Permissions:
            Must be logged in as the user or have `edit_other_users` permission.
        """

        url = "/channels/{channel_id}/members/{user_id}/notify_props".format(
            channel_id=channel_id,
            user_id=user_id,
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def view_channel(
        self,
        user_id: str,
        *,
        json_body: ViewChannelJsonBody,
    ) -> ViewChannelResponse_200:
        """View channel

        Perform all the actions involved in viewing a channel. This includes
        marking channels as read, clearing push notifications, and updating the
        active channel.

        __Response only includes `last_viewed_at_times` in Mattermost server 4.3
        and newer.__

        Permissions:
            Must be logged in as user or have `edit_other_users` permission.
        """

        url = "/channels/members/{user_id}/view".format(
            user_id=user_id,
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
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = ViewChannelResponse_200.parse_obj(response.json())

            return response_200
        return response

    def get_channel_members_for_user(
        self,
        user_id: str,
        team_id: str,
    ) -> List[ChannelMember]:
        """Get channel memberships and roles for a user

        Get all channel memberships and associated membership roles (i.e.
        `channel_user`, `channel_admin`) for a user on a specific team.

        Permissions:
            Logged in as the user and `view_team` permission for the team.
        Having `manage_system` permission voids the previous requirements.
        """

        url = "/users/{user_id}/teams/{team_id}/channels/members".format(
            user_id=user_id,
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = ChannelMember.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_channels_for_team_for_user(
        self,
        user_id: str,
        team_id: str,
        *,
        include_deleted: Optional[bool] = False,
        last_delete_at: Optional[int] = 0,
    ) -> List[Channel]:
        """Get channels for user

        Get all the channels on a team for a user.

        Permissions:
            Logged in as the user, or have `edit_other_users` permission, and
        `view_team` permission for the team.
        """

        url = "/users/{user_id}/teams/{team_id}/channels".format(
            user_id=user_id,
            team_id=team_id,
        )
        params: Dict[str, Any] = {
            "include_deleted": include_deleted,
            "last_delete_at": last_delete_at,
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
                response_200_item = Channel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_channels_for_user(
        self,
        user_id: str,
        *,
        last_delete_at: Optional[int] = 0,
        include_deleted: Optional[bool] = False,
    ) -> List[Channel]:
        """Get all channels from all teams

        Get all channels from all teams that a user is a member of.

        Permissions:
            Logged in as the user, or have `edit_other_users` permission.
        Minimum Server Version:
            6.1
        """

        url = "/users/{user_id}/channels".format(
            user_id=user_id,
        )
        params: Dict[str, Any] = {
            "last_delete_at": last_delete_at,
            "include_deleted": include_deleted,
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
                response_200_item = Channel.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_channel_unread(
        self,
        user_id: str,
        channel_id: str,
    ) -> ChannelUnread:
        """Get unread messages

        Get the total unread messages and mentions for a channel for a user.

        Permissions:
            Must be logged in as user and have the `read_channel` permission, or
        have `edit_other_usrs` permission.
        """

        url = "/users/{user_id}/channels/{channel_id}/unread".format(
            user_id=user_id,
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
            response_200 = ChannelUnread.parse_obj(response.json())

            return response_200
        return response

    def update_channel_scheme(
        self,
        channel_id: str,
        *,
        json_body: UpdateChannelSchemeJsonBody,
    ) -> StatusOK:
        """Set a channel's scheme

        Set a channel's scheme, more specifically sets the scheme_id value of a
        channel record.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.10
        """

        url = "/channels/{channel_id}/scheme".format(
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def channel_members_minus_group_members(
        self,
        channel_id: str,
        *,
        group_ids: str = "",
        page: Optional[int] = 0,
        per_page: Optional[int] = 0,
    ) -> None:
        """Channel members minus group members.

        Get the set of users who are members of the channel minus the set of
        users who are members of the given groups.
        Each user object contains an array of group objects representing the
        group memberships for that user.
        Each user object contains the boolean fields `scheme_guest`,
        `scheme_user`, and `scheme_admin` representing the roles that user has
        for the given channel.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.14
        """

        url = "/channels/{channel_id}/members_minus_group_members".format(
            channel_id=channel_id,
        )
        params: Dict[str, Any] = {
            "group_ids": group_ids,
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

        return response

    def get_channel_member_counts_by_group(
        self,
        channel_id: str,
        *,
        include_timezones: Optional[bool] = False,
    ) -> None:
        """Channel members counts for each group that has atleast one member in the
        channel

        Returns a set of ChannelMemberCountByGroup objects which contain a
        `group_id`, `channel_member_count` and a
        `channel_member_timezones_count`.

        Permissions:
            Must have `read_channel` permission for the given channel.
        Minimum Server Version:
            5.24
        """

        url = "/channels/{channel_id}/member_counts_by_group".format(
            channel_id=channel_id,
        )
        params: Dict[str, Any] = {
            "include_timezones": include_timezones,
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

        return response

    def get_channel_moderations(
        self,
        channel_id: str,
    ) -> List[ChannelModeration]:
        """Get information about channel's moderation.



        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.22
        """

        url = "/channels/{channel_id}/moderations".format(
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = ChannelModeration.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def patch_channel_moderations(
        self,
        channel_id: str,
        *,
        json_body: ChannelModerationPatch,
    ) -> List[ChannelModeration]:
        """Update a channel's moderation settings.



        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.22
        """

        url = "/channels/{channel_id}/moderations/patch".format(
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = ChannelModeration.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_sidebar_categories_for_team_for_user(
        self,
        team_id: str,
        user_id: str,
    ) -> List[OrderedSidebarCategories]:
        """Get user's sidebar categories

        Get a list of sidebar categories that will appear in the user's sidebar
        on the given team, including a list of channel IDs in each category.

        Permissions:
            Must be authenticated and have the `list_team_channels` permission.
        Minimum Server Version:
            5.26
        """

        url = "/users/{user_id}/teams/{team_id}/channels/categories".format(
            team_id=team_id,
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
                response_200_item = OrderedSidebarCategories.parse_obj(
                    response_200_item_data
                )

                response_200.append(response_200_item)

            return response_200
        return response

    def update_sidebar_categories_for_team_for_user(
        self,
        team_id: str,
        user_id: str,
        *,
        json_body: List[SidebarCategory],
    ) -> SidebarCategory:
        """Update user's sidebar categories

        Update any number of sidebar categories for the user on the given team.
        This can be used to reorder the channels in these categories.

        Permissions:
            Must be authenticated and have the `list_team_channels` permission.
        Minimum Server Version:
            5.26
        """

        url = "/users/{user_id}/teams/{team_id}/channels/categories".format(
            team_id=team_id,
            user_id=user_id,
        )
        json_json_body = []
        for json_body_item_data in json_body:

            if isinstance(json_body_item_data, BaseModel):
                json_body_item = json_body_item_data.dict(exclude_unset=True)
            else:
                json_body_item = json_body_item_data

            json_json_body.append(json_body_item)

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
            response_200 = SidebarCategory.parse_obj(response.json())

            return response_200
        return response

    def create_sidebar_category_for_team_for_user(
        self,
        team_id: str,
        user_id: str,
        *,
        json_body: SidebarCategory,
    ) -> SidebarCategory:
        """Create user's sidebar category

        Create a custom sidebar category for the user on the given team.

        Permissions:
            Must be authenticated and have the `list_team_channels` permission.
        Minimum Server Version:
            5.26
        """

        url = "/users/{user_id}/teams/{team_id}/channels/categories".format(
            team_id=team_id,
            user_id=user_id,
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
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = SidebarCategory.parse_obj(response.json())

            return response_200
        return response

    def get_sidebar_category_order_for_team_for_user(
        self,
        team_id: str,
        user_id: str,
    ) -> List[str]:
        """Get user's sidebar category order

        Returns the order of the sidebar categories for a user on the given team
        as an array of IDs.

        Permissions:
            Must be authenticated and have the `list_team_channels` permission.
        Minimum Server Version:
            5.26
        """

        url = "/users/{user_id}/teams/{team_id}/channels/categories/order".format(
            team_id=team_id,
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
            response_200 = cast(List[str], response.json())

            return response_200
        return response

    def update_sidebar_category_order_for_team_for_user(
        self,
        team_id: str,
        user_id: str,
        *,
        json_body: List[str],
    ) -> List[str]:
        """Update user's sidebar category order

        Updates the order of the sidebar categories for a user on the given
        team. The provided array must include the IDs of all categories on the
        team.

        Permissions:
            Must be authenticated and have the `list_team_channels` permission.
        Minimum Server Version:
            5.26
        """

        url = "/users/{user_id}/teams/{team_id}/channels/categories/order".format(
            team_id=team_id,
            user_id=user_id,
        )
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
            response_200 = cast(List[str], response.json())

            return response_200
        return response

    def get_sidebar_category_for_team_for_user(
        self,
        team_id: str,
        user_id: str,
        category_id: str,
    ) -> SidebarCategory:
        """Get sidebar category

        Returns a single sidebar category for the user on the given team.

        Permissions:
            Must be authenticated and have the `list_team_channels` permission.
        Minimum Server Version:
            5.26
        """

        url = (
            "/users/{user_id}/teams/{team_id}/channels/categories/{category_id}".format(
                team_id=team_id,
                user_id=user_id,
                category_id=category_id,
            )
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
            response_200 = SidebarCategory.parse_obj(response.json())

            return response_200
        return response

    def update_sidebar_category_for_team_for_user(
        self,
        team_id: str,
        user_id: str,
        category_id: str,
        *,
        json_body: SidebarCategory,
    ) -> SidebarCategory:
        """Update sidebar category

        Updates a single sidebar category for the user on the given team.

        Permissions:
            Must be authenticated and have the `list_team_channels` permission.
        Minimum Server Version:
            5.26
        """

        url = (
            "/users/{user_id}/teams/{team_id}/channels/categories/{category_id}".format(
                team_id=team_id,
                user_id=user_id,
                category_id=category_id,
            )
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
            response_200 = SidebarCategory.parse_obj(response.json())

            return response_200
        return response

    def remove_sidebar_category_for_team_for_user(
        self,
        team_id: str,
        user_id: str,
        category_id: str,
    ) -> SidebarCategory:
        """Delete sidebar category

        Deletes a single sidebar category for the user on the given team. Only
        custom categories can be deleted.

        Permissions:
            Must be authenticated and have the `list_team_channels` permission.
        Minimum Server Version:
            5.26
        """

        url = (
            "/users/{user_id}/teams/{team_id}/channels/categories/{category_id}".format(
                team_id=team_id,
                user_id=user_id,
                category_id=category_id,
            )
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
            response_200 = SidebarCategory.parse_obj(response.json())

            return response_200
        return response
