from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ...models import (
    ChannelListWithTeamData,
    DataRetentionPolicyCreate,
    DataRetentionPolicyWithTeamAndChannelCounts,
    DataRetentionPolicyWithTeamAndChannelIds,
    GetDataRetentionPoliciesCountResponse_200,
    GlobalDataRetentionPolicy,
    RetentionPolicyForChannelList,
    RetentionPolicyForTeamList,
    SearchChannelsForRetentionPolicyJsonBody,
    SearchTeamsForRetentionPolicyJsonBody,
    StatusOK,
    Team,
)
from ..base import ApiBaseClass


class DataRetentionApi(ApiBaseClass):
    """Endpoint for getting data retention policy settings."""

    async def get_team_policies_for_user(
        self,
        user_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> RetentionPolicyForTeamList:
        """Get the policies which are applied to a user's teams

        Gets the policies which are applied to the all of the teams to which a
        user belongs.

        ##### License
        Requires an E20 license.

        Permissions:
            Must be logged in as the user or have the `manage_system`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/users/{user_id}/data_retention/team_policies".format(
            user_id=user_id,
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = RetentionPolicyForTeamList.parse_obj(response.json())

            return response_200
        return response

    async def get_channel_policies_for_user(
        self,
        user_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> RetentionPolicyForChannelList:
        """Get the policies which are applied to a user's channels

        Gets the policies which are applied to the all of the channels to which
        a user belongs.

        ##### License
        Requires an E20 license.

        Permissions:
            Must be logged in as the user or have the `manage_system`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/users/{user_id}/data_retention/channel_policies".format(
            user_id=user_id,
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = RetentionPolicyForChannelList.parse_obj(response.json())

            return response_200
        return response

    async def get_data_retention_policy(
        self,
    ) -> GlobalDataRetentionPolicy:
        """Get the global data retention policy

        Gets the current global data retention policy details from the server,
        including what data should be purged and the cutoff times for each data
        type that should be purged.

        ##### License
        Requires an E20 license.

        Permissions:
            Requires an active session but no other permissions.
        Minimum Server Version:
            4.3
        """

        url = "/data_retention/policy".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GlobalDataRetentionPolicy.parse_obj(response.json())

            return response_200
        return response

    async def get_data_retention_policies_count(
        self,
    ) -> GetDataRetentionPoliciesCountResponse_200:
        """Get the number of granular data retention policies

        Gets the number of granular (i.e. team or channel-specific) data
        retention
        policies from the server.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_read_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies_count".format()

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = GetDataRetentionPoliciesCountResponse_200.parse_obj(
                response.json()
            )

            return response_200
        return response

    async def get_data_retention_policies(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[DataRetentionPolicyWithTeamAndChannelCounts]:
        """Get the granular data retention policies

        Gets details about the granular (i.e. team or channel-specific) data
        retention
        policies from the server.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_read_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies".format()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = (
                    DataRetentionPolicyWithTeamAndChannelCounts.parse_obj(
                        response_200_item_data
                    )
                )

                response_200.append(response_200_item)

            return response_200
        return response

    async def create_data_retention_policy(
        self,
        *,
        json_body: DataRetentionPolicyCreate,
    ) -> DataRetentionPolicyWithTeamAndChannelCounts:
        """Create a new granular data retention policy

        Creates a new granular data retention policy with the specified display
        name and post duration.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_write_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies".format()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = DataRetentionPolicyWithTeamAndChannelCounts.parse_obj(
                response.json()
            )

            return response_201
        return response

    async def get_data_retention_policy_by_id(
        self,
        policy_id: str,
    ) -> DataRetentionPolicyWithTeamAndChannelCounts:
        """Get a granular data retention policy

        Gets details about a granular data retention policies by ID.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_read_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}".format(
            policy_id=policy_id,
        )

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = DataRetentionPolicyWithTeamAndChannelCounts.parse_obj(
                response.json()
            )

            return response_200
        return response

    async def delete_data_retention_policy(
        self,
        policy_id: str,
    ) -> StatusOK:
        """Delete a granular data retention policy

        Deletes a granular data retention policy.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_write_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}".format(
            policy_id=policy_id,
        )

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def patch_data_retention_policy(
        self,
        policy_id: str,
        *,
        json_body: DataRetentionPolicyWithTeamAndChannelIds,
    ) -> DataRetentionPolicyWithTeamAndChannelCounts:
        """Patch a granular data retention policy

        Patches (i.e. replaces the fields of) a granular data retention policy.
        If any fields are omitted, they will not be changed.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_write_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}".format(
            policy_id=policy_id,
        )

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.patch(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = DataRetentionPolicyWithTeamAndChannelCounts.parse_obj(
                response.json()
            )

            return response_200
        return response

    async def get_teams_for_retention_policy(
        self,
        policy_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[Team]:
        """Get the teams for a granular data retention policy

        Gets the teams to which a granular data retention policy is applied.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_read_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}/teams".format(
            policy_id=policy_id,
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Team.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def add_teams_to_retention_policy(
        self,
        policy_id: str,
        *,
        json_body: List[str],
    ) -> StatusOK:
        """Add teams to a granular data retention policy

        Adds teams to a granular data retention policy.



        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_write_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}/teams".format(
            policy_id=policy_id,
        )
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def remove_teams_from_retention_policy(
        self,
        policy_id: str,
        *,
        json_body: List[str],
    ) -> StatusOK:
        """Delete teams from a granular data retention policy

        Delete teams from a granular data retention policy.



        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_write_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}/teams".format(
            policy_id=policy_id,
        )
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def search_teams_for_retention_policy(
        self,
        policy_id: str,
        *,
        json_body: SearchTeamsForRetentionPolicyJsonBody,
    ) -> List[Team]:
        """Search for the teams in a granular data retention policy

        Searches for the teams to which a granular data retention policy is
        applied.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_read_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}/teams/search".format(
            policy_id=policy_id,
        )

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Team.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def get_channels_for_retention_policy(
        self,
        policy_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> ChannelListWithTeamData:
        """Get the channels for a granular data retention policy

        Gets the channels to which a granular data retention policy is applied.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_read_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}/channels".format(
            policy_id=policy_id,
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = ChannelListWithTeamData.parse_obj(response.json())

            return response_200
        return response

    async def add_channels_to_retention_policy(
        self,
        policy_id: str,
        *,
        json_body: List[str],
    ) -> StatusOK:
        """Add channels to a granular data retention policy

        Adds channels to a granular data retention policy.



        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_write_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}/channels".format(
            policy_id=policy_id,
        )
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def remove_channels_from_retention_policy(
        self,
        policy_id: str,
        *,
        json_body: List[str],
    ) -> StatusOK:
        """Delete channels from a granular data retention policy

        Delete channels from a granular data retention policy.



        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_write_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}/channels".format(
            policy_id=policy_id,
        )
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def search_channels_for_retention_policy(
        self,
        policy_id: str,
        *,
        json_body: SearchChannelsForRetentionPolicyJsonBody,
    ) -> ChannelListWithTeamData:
        """Search for the channels in a granular data retention policy

        Searches for the channels to which a granular data retention policy is
        applied.

        ##### License
        Requires an E20 license.

        Permissions:
            Must have the `sysconsole_read_compliance_data_retention`
        permission.
        Minimum Server Version:
            5.35
        """

        url = "/data_retention/policies/{policy_id}/channels/search".format(
            policy_id=policy_id,
        )

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = ChannelListWithTeamData.parse_obj(response.json())

            return response_200
        return response
