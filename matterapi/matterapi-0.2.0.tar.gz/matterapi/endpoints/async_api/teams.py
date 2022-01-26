from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ...models import (
    AddTeamMemberJsonBody,
    CreateTeamJsonBody,
    FileInfoList,
    GetTeamInviteInfoResponse_200,
    ImportTeamMultipartData,
    ImportTeamResponse_200,
    InviteGuestsToTeamJsonBody,
    PatchTeamJsonBody,
    SearchFilesMultipartData,
    SearchTeamsJsonBody,
    SearchTeamsResponse_200,
    SetTeamIconMultipartData,
    StatusOK,
    Team,
    TeamExists,
    TeamMember,
    TeamStats,
    TeamUnread,
    UpdateTeamJsonBody,
    UpdateTeamMemberRolesJsonBody,
    UpdateTeamMemberSchemeRolesJsonBody,
    UpdateTeamPrivacyJsonBody,
    UpdateTeamSchemeJsonBody,
)
from ..base import ApiBaseClass


class TeamsApi(ApiBaseClass):
    """Endpoints for creating, getting and interacting with teams."""

    async def get_all_teams(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
        include_total_count: Optional[bool] = False,
        exclude_policy_constrained: Optional[bool] = False,
    ) -> List[Team]:
        """Get teams

        For regular users only returns open teams. Users with the
        \"manage_system\" permission will return teams regardless of type. The
        result is based on query string parameters - page and per_page.

        Permissions:
            Must be authenticated. \"manage_system\" permission is required to
        show all teams.
        """

        url = "/teams".format()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "include_total_count": include_total_count,
            "exclude_policy_constrained": exclude_policy_constrained,
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

    async def create_team(
        self,
        *,
        json_body: CreateTeamJsonBody,
    ) -> Team:
        """Create a team

        Create a new team on the system.

        Permissions:
            Must be authenticated and have the `create_team` permission.
        """

        url = "/teams".format()

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
            response_201 = Team.parse_obj(response.json())

            return response_201
        return response

    async def get_team(
        self,
        team_id: str,
    ) -> Team:
        """Get a team

        Get a team on the system.

        Permissions:
            Must be authenticated and have the `view_team` permission.
        """

        url = "/teams/{team_id}".format(
            team_id=team_id,
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
            response_200 = Team.parse_obj(response.json())

            return response_200
        return response

    async def update_team(
        self,
        team_id: str,
        *,
        json_body: UpdateTeamJsonBody,
    ) -> Team:
        """Update a team

        Update a team by providing the team object. The fields that can be
        updated are defined in the request body, all other provided fields will
        be ignored.

        Permissions:
            Must have the `manage_team` permission.
        """

        url = "/teams/{team_id}".format(
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Team.parse_obj(response.json())

            return response_200
        return response

    async def soft_delete_team(
        self,
        team_id: str,
        *,
        permanent: Optional[bool] = False,
    ) -> StatusOK:
        """Delete a team

        Soft deletes a team, by marking the team as deleted in the database.
        Soft deleted teams will not be accessible in the user interface.

        Optionally use the permanent query parameter to hard delete the team for
        compliance reasons. As of server version 5.0, to use this feature
        `ServiceSettings.EnableAPITeamDeletion` must be set to `true` in the
        server's configuration.

        Permissions:
            Must have the `manage_team` permission.
        """

        url = "/teams/{team_id}".format(
            team_id=team_id,
        )
        params: Dict[str, Any] = {
            "permanent": permanent,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
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

    async def patch_team(
        self,
        team_id: str,
        *,
        json_body: PatchTeamJsonBody,
    ) -> Team:
        """Patch a team

        Partially update a team by providing only the fields you want to update.
        Omitted fields will not be updated. The fields that can be updated are
        defined in the request body, all other provided fields will be ignored.

        Permissions:
            Must have the `manage_team` permission.
        """

        url = "/teams/{team_id}/patch".format(
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Team.parse_obj(response.json())

            return response_200
        return response

    async def update_team_privacy(
        self,
        team_id: str,
        *,
        json_body: UpdateTeamPrivacyJsonBody,
    ) -> Team:
        """Update teams's privacy

        Updates team's privacy allowing changing a team from Public (open) to
        Private (invitation only) and back.

        Permissions:
            `manage_team` permission for the team of the team.
        Minimum Server Version:
            5.24
        """

        url = "/teams/{team_id}/privacy".format(
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Team.parse_obj(response.json())

            return response_200
        return response

    async def restore_team(
        self,
        team_id: str,
    ) -> Team:
        """Restore a team

        Restore a team that was previously soft deleted.

        Permissions:
            Must have the `manage_team` permission.
        Minimum Server Version:
            5.24
        """

        url = "/teams/{team_id}/restore".format(
            team_id=team_id,
        )

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Team.parse_obj(response.json())

            return response_200
        return response

    async def get_team_by_name(
        self,
        name: str,
    ) -> Team:
        """Get a team by name

        Get a team based on provided name string

        Permissions:
            Must be authenticated, team type is open and have the `view_team`
        permission.
        """

        url = "/teams/name/{name}".format(
            name=name,
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
            response_200 = Team.parse_obj(response.json())

            return response_200
        return response

    async def search_teams(
        self,
        *,
        json_body: SearchTeamsJsonBody,
    ) -> SearchTeamsResponse_200:
        """Search teams

        Search teams based on search term and options provided in the request
        body.

        Logged in user with \"manage_system\" permission shows all teams

        Permissions:
            Logged in user only shows open teams
        """

        url = "/teams/search".format()

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
            response_200 = SearchTeamsResponse_200.parse_obj(response.json())

            return response_200
        return response

    async def team_exists(
        self,
        name: str,
    ) -> TeamExists:
        """Check if team exists

        Check if the team exists based on a team name.

        Permissions:
            Must be authenticated.
        """

        url = "/teams/name/{name}/exists".format(
            name=name,
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
            response_200 = TeamExists.parse_obj(response.json())

            return response_200
        return response

    async def get_teams_for_user(
        self,
        user_id: str,
    ) -> List[Team]:
        """Get a user's teams

        Get a list of teams that a user is on.

        Permissions:
            Must be authenticated as the user or have the `manage_system`
        permission.
        """

        url = "/users/{user_id}/teams".format(
            user_id=user_id,
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Team.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def get_team_members(
        self,
        team_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[TeamMember]:
        """Get team members

        Get a page team members list based on query string parameters - team id,
        page and per page.

        Permissions:
            Must be authenticated and have the `view_team` permission.
        """

        url = "/teams/{team_id}/members".format(
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
                response_200_item = TeamMember.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def add_team_member(
        self,
        team_id: str,
        *,
        json_body: AddTeamMemberJsonBody,
    ) -> TeamMember:
        """Add user to team

        Add user to the team by user_id.

        Permissions:
            Must be authenticated and team be open to add self. For adding
        another user, authenticated user must have the `add_user_to_team`
        permission.
        """

        url = "/teams/{team_id}/members".format(
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = TeamMember.parse_obj(response.json())

            return response_201
        return response

    async def add_team_member_from_invite(
        self,
        *,
        token: str,
    ) -> TeamMember:
        """Add user to team from invite

        Using either an invite id or hash/data pair from an email invite link,
        add a user to a team.

        Permissions:
            Must be authenticated.
        """

        url = "/teams/members/invite".format()
        params: Dict[str, Any] = {
            "token": token,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "params": params,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = TeamMember.parse_obj(response.json())

            return response_201
        return response

    async def add_team_members(
        self,
        team_id: str,
        *,
        json_body: List[TeamMember],
        graceful: Optional[bool] = None,
    ) -> List[TeamMember]:
        """Add multiple users to team

        Add a number of users to the team by user_id.

        Permissions:
            Must be authenticated. Authenticated user must have the
        `add_user_to_team` permission.
        """

        url = "/teams/{team_id}/members/batch".format(
            team_id=team_id,
        )
        params: Dict[str, Any] = {
            "graceful": graceful,
        }
        params = {k: v for k, v in params.items() if v is not None}

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
            "params": params,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = []
            _response_201 = response.json()
            for response_201_item_data in _response_201:
                response_201_item = TeamMember.parse_obj(response_201_item_data)

                response_201.append(response_201_item)

            return response_201
        return response

    async def get_team_members_for_user(
        self,
        user_id: str,
    ) -> List[TeamMember]:
        """Get team members for a user

        Get a list of team members for a user. Useful for getting the ids of
        teams the user is on and the roles they have in those teams.

        Permissions:
            Must be logged in as the user or have the `edit_other_users`
        permission.
        """

        url = "/users/{user_id}/teams/members".format(
            user_id=user_id,
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = TeamMember.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def get_team_member(
        self,
        team_id: str,
        user_id: str,
    ) -> TeamMember:
        """Get a team member

        Get a team member on the system.

        Permissions:
            Must be authenticated and have the `view_team` permission.
        """

        url = "/teams/{team_id}/members/{user_id}".format(
            team_id=team_id,
            user_id=user_id,
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
            response_200 = TeamMember.parse_obj(response.json())

            return response_200
        return response

    async def remove_team_member(
        self,
        team_id: str,
        user_id: str,
    ) -> StatusOK:
        """Remove user from team

        Delete the team member object for a user, effectively removing them from
        a team.

        Permissions:
            Must be logged in as the user or have the `remove_user_from_team`
        permission.
        """

        url = "/teams/{team_id}/members/{user_id}".format(
            team_id=team_id,
            user_id=user_id,
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

    async def get_team_members_by_ids(
        self,
        team_id: str,
        *,
        json_body: List[str],
    ) -> List[TeamMember]:
        """Get team members by ids

        Get a list of team members based on a provided array of user ids.

        Permissions:
            Must have `view_team` permission for the team.
        """

        url = "/teams/{team_id}/members/ids".format(
            team_id=team_id,
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = TeamMember.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def get_team_stats(
        self,
        team_id: str,
    ) -> TeamStats:
        """Get a team stats

        Get a team stats on the system.

        Permissions:
            Must be authenticated and have the `view_team` permission.
        """

        url = "/teams/{team_id}/stats".format(
            team_id=team_id,
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
            response_200 = TeamStats.parse_obj(response.json())

            return response_200
        return response

    async def regenerate_team_invite_id(
        self,
        team_id: str,
    ) -> Team:
        """Regenerate the Invite ID from a Team

        Regenerates the invite ID used in invite links of a team

        Permissions:
            Must be authenticated and have the `manage_team` permission.
        """

        url = "/teams/{team_id}/regenerate_invite_id".format(
            team_id=team_id,
        )

        request_kwargs = {
            "url": url,
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Team.parse_obj(response.json())

            return response_200
        return response

    async def get_team_icon(
        self,
        team_id: str,
    ) -> None:
        """Get the team icon

        Get the team icon of the team.

        Permissions:
            User must be authenticated. In addition, team must be open or the
        user must have the `view_team` permission.
        Minimum Server Version:
            4.9
        """

        url = "/teams/{team_id}/image".format(
            team_id=team_id,
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

        return response

    async def set_team_icon(
        self,
        team_id: str,
        *,
        multipart_data: SetTeamIconMultipartData,
    ) -> StatusOK:
        """Sets the team icon

        Sets the team icon for the team.

        Permissions:
            Must be authenticated and have the `manage_team` permission.
        Minimum Server Version:
            4.9
        """

        url = "/teams/{team_id}/image".format(
            team_id=team_id,
        )

        multipart_body_data = SetTeamIconMultipartData.parse_obj(multipart_data)

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
            "files": multipart_body_data.get_files(),
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

    async def remove_team_icon(
        self,
        team_id: str,
    ) -> StatusOK:
        """Remove the team icon

        Remove the team icon for the team.

        Permissions:
            Must be authenticated and have the `manage_team` permission.
        Minimum Server Version:
            4.10
        """

        url = "/teams/{team_id}/image".format(
            team_id=team_id,
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

    async def update_team_member_roles(
        self,
        team_id: str,
        user_id: str,
        *,
        json_body: UpdateTeamMemberRolesJsonBody,
    ) -> StatusOK:
        """Update a team member roles

        Update a team member roles. Valid team roles are \"team_user\",
        \"team_admin\" or both of them. Overwrites any previously assigned team
        roles.

        Permissions:
            Must be authenticated and have the `manage_team_roles` permission.
        """

        url = "/teams/{team_id}/members/{user_id}/roles".format(
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def update_team_member_scheme_roles(
        self,
        team_id: str,
        user_id: str,
        *,
        json_body: UpdateTeamMemberSchemeRolesJsonBody,
    ) -> StatusOK:
        """Update the scheme-derived roles of a team member.

        Update a team member's scheme_admin/scheme_user properties. Typically
        this should either be `scheme_admin=false, scheme_user=true` for
        ordinary team member, or `scheme_admin=true, scheme_user=true` for a
        team admin.

        Permissions:
            Must be authenticated and have the `manage_team_roles` permission.
        Minimum Server Version:
            5.0
        """

        url = "/teams/{team_id}/members/{user_id}/schemeRoles".format(
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def get_teams_unread_for_user(
        self,
        user_id: str,
        *,
        exclude_team: str,
    ) -> List[TeamUnread]:
        """Get team unreads for a user

        Get the count for unread messages and mentions in the teams the user is
        a member of.

        Permissions:
            Must be logged in.
        """

        url = "/users/{user_id}/teams/unread".format(
            user_id=user_id,
        )
        params: Dict[str, Any] = {
            "exclude_team": exclude_team,
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
                response_200_item = TeamUnread.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def get_team_unread(
        self,
        user_id: str,
        team_id: str,
    ) -> TeamUnread:
        """Get unreads for a team

        Get the unread mention and message counts for a team for the specified
        user.

        Permissions:
            Must be the user or have `edit_other_users` permission and have
        `view_team` permission for the team.
        """

        url = "/users/{user_id}/teams/{team_id}/unread".format(
            user_id=user_id,
            team_id=team_id,
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
            response_200 = TeamUnread.parse_obj(response.json())

            return response_200
        return response

    async def invite_users_to_team(
        self,
        team_id: str,
        *,
        json_body: List[str],
    ) -> StatusOK:
        """Invite users to the team by email

        Invite users to the existing team using the user's email.

        The number of emails that can be sent is rate limited to 20 per hour
        with a burst of 20 emails. If the rate limit exceeds, the error message
        contains details on when to retry and when the timer will be reset.

        Permissions:
            Must have `invite_user` and `add_user_to_team` permissions for the
        team.
        """

        url = "/teams/{team_id}/invite/email".format(
            team_id=team_id,
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

    async def invite_guests_to_team(
        self,
        team_id: str,
        *,
        json_body: InviteGuestsToTeamJsonBody,
    ) -> StatusOK:
        """Invite guests to the team by email

        Invite guests to existing team channels usign the user's email.

        The number of emails that can be sent is rate limited to 20 per hour
        with a burst of 20 emails. If the rate limit exceeds, the error message
        contains details on when to retry and when the timer will be reset.

        Permissions:
            Must have `invite_guest` permission for the team.
        Minimum Server Version:
            5.16
        """

        url = "/teams/{team_id}/invite-guests/email".format(
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

    async def invalidate_email_invites(
        self,
    ) -> StatusOK:
        """Invalidate active email invitations

        Invalidate active email invitations that have not been accepted by the
        user.

        Permissions:
            Must have `sysconsole_write_authentication` permission.
        """

        url = "/teams/invites/email".format()

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

    async def import_team(
        self,
        team_id: str,
        *,
        multipart_data: ImportTeamMultipartData,
    ) -> ImportTeamResponse_200:
        """Import a Team from other application

        Import a team into a existing team. Import users, channels, posts,
        hooks.

        Permissions:
            Must have `permission_import_team` permission.
        """

        url = "/teams/{team_id}/import".format(
            team_id=team_id,
        )

        multipart_body_data = ImportTeamMultipartData.parse_obj(multipart_data)

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
            "files": multipart_body_data.get_files(),
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = ImportTeamResponse_200.parse_obj(response.json())

            return response_200
        return response

    async def get_team_invite_info(
        self,
        invite_id: str,
    ) -> GetTeamInviteInfoResponse_200:
        """Get invite info for a team

        Get the `name`, `display_name`, `description` and `id` for a team from
        the invite id.

        Permissions:
            No authentication required.
        Minimum Server Version:
            4.0
        """

        url = "/teams/invite/{invite_id}".format(
            invite_id=invite_id,
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
            response_200 = GetTeamInviteInfoResponse_200.parse_obj(response.json())

            return response_200
        return response

    async def update_team_scheme(
        self,
        team_id: str,
        *,
        json_body: UpdateTeamSchemeJsonBody,
    ) -> StatusOK:
        """Set a team's scheme

        Set a team's scheme, more specifically sets the scheme_id value of a
        team record.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.0
        """

        url = "/teams/{team_id}/scheme".format(
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.put(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def team_members_minus_group_members(
        self,
        team_id: str,
        *,
        group_ids: str = "",
        page: Optional[int] = 0,
        per_page: Optional[int] = 0,
    ) -> None:
        """Team members minus group members.

        Get the set of users who are members of the team minus the set of users
        who are members of the given groups.
        Each user object contains an array of group objects representing the
        group memberships for that user.
        Each user object contains the boolean fields `scheme_guest`,
        `scheme_user`, and `scheme_admin` representing the roles that user has
        for the given team.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.14
        """

        url = "/teams/{team_id}/members_minus_group_members".format(
            team_id=team_id,
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

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.get(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    async def search_files(
        self,
        team_id: str,
        *,
        multipart_data: SearchFilesMultipartData,
    ) -> FileInfoList:
        """Search files in a team

        Search for files in a team based on file name, extention and file
        content (if file content extraction is enabled and supported for the
        files).

        Permissions:
            Must be authenticated and have the `view_team` permission.
        Minimum Server Version:
            5.34
        """

        url = "/teams/{team_id}/files/search".format(
            team_id=team_id,
        )

        multipart_body_data = SearchFilesMultipartData.parse_obj(multipart_data)

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
        }

        async with self.client._get_httpx_client() as httpx_client:
            response = await httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = FileInfoList.parse_obj(response.json())

            return response_200
        return response
