from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from ...models import (
    AppError,
    AttachDeviceIdJsonBody,
    Audit,
    ChannelMemberWithTeamData,
    CheckUserMfaJsonBody,
    CheckUserMfaResponse_200,
    ConvertBotToUserJsonBody,
    CreateUserAccessTokenJsonBody,
    CreateUserJsonBody,
    DisableUserAccessTokenJsonBody,
    EnableUserAccessTokenJsonBody,
    GenerateMfaSecretResponse_200,
    GetUsersByGroupChannelIdsResponse_200,
    LoginByCwsTokenJsonBody,
    LoginJsonBody,
    MigrateAuthToLdapJsonBody,
    MigrateAuthToSamlJsonBody,
    PatchUserJsonBody,
    PublishUserTypingJsonBody,
    RegisterTermsOfServiceActionJsonBody,
    ResetPasswordJsonBody,
    RevokeSessionJsonBody,
    RevokeUserAccessTokenJsonBody,
    SearchUserAccessTokensJsonBody,
    SearchUsersJsonBody,
    SendPasswordResetEmailJsonBody,
    SendVerificationEmailJsonBody,
    Session,
    SetProfileImageMultipartData,
    StatusOK,
    SwitchAccountTypeJsonBody,
    SwitchAccountTypeResponse_200,
    UpdateUserActiveJsonBody,
    UpdateUserJsonBody,
    UpdateUserMfaJsonBody,
    UpdateUserPasswordJsonBody,
    UpdateUserRolesJsonBody,
    UploadSession,
    User,
    UserAccessToken,
    UserAccessTokenSanitized,
    UserAuthData,
    UserAutocomplete,
    UsersStats,
    UserTermsOfService,
    VerifyUserEmailJsonBody,
)
from ..base import ApiBaseClass


class UsersApi(ApiBaseClass):
    """Endpoints for creating, getting and interacting with users.

    When using endpoints that require a user id, the string `me` can be used
    in place of the user id to indicate the action is to be taken for the
    logged in user."""

    def login(
        self,
        *,
        json_body: LoginJsonBody,
    ) -> User:
        """Login to Mattermost server



        Permissions:
            No permission required
        """

        url = "/users/login".format()

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
            response_201 = User.parse_obj(response.json())

            return response_201
        return response

    def login_by_cws_token(
        self,
        *,
        json_body: LoginByCwsTokenJsonBody,
    ) -> None:
        """Auto-Login to Mattermost server using CWS token

        CWS stands for Customer Web Server which is the cloud service used to
        manage cloud instances.

        Permissions:
            A Cloud license is required
        """

        url = "/users/login/cws".format()

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

        return response

    def logout(
        self,
    ) -> StatusOK:
        """Logout from the Mattermost server



        Permissions:
            An active session is required
        """

        url = "/users/logout".format()

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
            response_201 = StatusOK.parse_obj(response.json())

            return response_201
        return response

    def get_users(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
        in_team: Optional[str] = None,
        not_in_team: Optional[str] = None,
        in_channel: Optional[str] = None,
        not_in_channel: Optional[str] = None,
        in_group: Optional[str] = None,
        group_constrained: Optional[bool] = None,
        without_team: Optional[bool] = None,
        active: Optional[bool] = None,
        inactive: Optional[bool] = None,
        role: Optional[str] = None,
        sort: Optional[str] = None,
        roles: Optional[str] = None,
        channel_roles: Optional[str] = None,
        team_roles: Optional[str] = None,
    ) -> List[User]:
        """Get users

        Get a page of a list of users. Based on query string parameters, select
        users from a team, channel, or select users not in a specific channel.

        Since server version 4.0, some basic sorting is available using the
        `sort` query parameter. Sorting is currently only supported when
        selecting users on a team.

        Permissions:
            Requires an active session and (if specified) membership to the
        channel or team being selected from.
        """

        url = "/users".format()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "in_team": in_team,
            "not_in_team": not_in_team,
            "in_channel": in_channel,
            "not_in_channel": not_in_channel,
            "in_group": in_group,
            "group_constrained": group_constrained,
            "without_team": without_team,
            "active": active,
            "inactive": inactive,
            "role": role,
            "sort": sort,
            "roles": roles,
            "channel_roles": channel_roles,
            "team_roles": team_roles,
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
                response_200_item = User.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def create_user(
        self,
        *,
        json_body: CreateUserJsonBody,
        t: Optional[str] = None,
        iid: Optional[str] = None,
    ) -> User:
        """Create a user

        Create a new user on the system. Password is required for email login.
        For other authentication types such as LDAP or SAML, auth_data and
        auth_service fields are required.

        Permissions:
            No permission required but user creation can be controlled by server
        configuration.
        """

        url = "/users".format()
        params: Dict[str, Any] = {
            "t": t,
            "iid": iid,
        }
        params = {k: v for k, v in params.items() if v is not None}

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = User.parse_obj(response.json())

            return response_201
        return response

    def permanent_delete_all_users(
        self,
    ) -> None:
        """Permanent delete all users

        Permanently deletes all users and all their related information,
        including posts.

        Minimum Server Version:
            5.26.0
        Local Mode Only:
            This endpoint is only available through [local
        mode](https://docs.mattermost.com/administration/mmctl-cli-
        tool.html#local-mode).
        """

        url = "/users".format()

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.delete(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    def get_users_by_ids(
        self,
        *,
        json_body: List[str],
        since: Optional[int] = None,
    ) -> List[User]:
        """Get users by ids

        Get a list of users based on a provided list of user ids.

        Permissions:
            Requires an active session but no other permissions.
        """

        url = "/users/ids".format()
        params: Dict[str, Any] = {
            "since": since,
        }
        params = {k: v for k, v in params.items() if v is not None}

        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
            "params": params,
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
                response_200_item = User.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_users_by_group_channel_ids(
        self,
        *,
        json_body: List[str],
    ) -> GetUsersByGroupChannelIdsResponse_200:
        """Get users by group channels ids

        Get an object containing a key per group channel id in the
        query and its value as a list of users members of that group
        channel.

        The user must be a member of the group ids in the query, or
        they will be omitted from the response.

        Permissions:
            Requires an active session but no other permissions.
        Minimum Server Version:
            5.14
        """

        url = "/users/group_channels".format()
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
            response_200 = GetUsersByGroupChannelIdsResponse_200.parse_obj(
                response.json()
            )

            return response_200
        return response

    def get_users_by_usernames(
        self,
        *,
        json_body: List[str],
    ) -> List[User]:
        """Get users by usernames

        Get a list of users based on a provided list of usernames.

        Permissions:
            Requires an active session but no other permissions.
        """

        url = "/users/usernames".format()
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
                response_200_item = User.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def search_users(
        self,
        *,
        json_body: SearchUsersJsonBody,
    ) -> List[User]:
        """Search users

        Get a list of users based on search criteria provided in the request
        body. Searches are typically done against username, full name, nickname
        and email unless otherwise configured by the server.

        Permissions:
            Requires an active session and `read_channel` and/or `view_team`
        permissions for any channels or teams specified in the request body.
        """

        url = "/users/search".format()

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
                response_200_item = User.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def autocomplete_users(
        self,
        *,
        team_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        name: str,
        limit: Optional[int] = 100,
    ) -> UserAutocomplete:
        """Autocomplete users

        Get a list of users for the purpose of autocompleting based on the
        provided search term. Specify a combination of `team_id` and
        `channel_id` to filter results further.

        Permissions:
            Requires an active session and `view_team` and `read_channel` on any
        teams or channels used to filter the results further.
        """

        url = "/users/autocomplete".format()
        params: Dict[str, Any] = {
            "team_id": team_id,
            "channel_id": channel_id,
            "name": name,
            "limit": limit,
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
            response_200 = UserAutocomplete.parse_obj(response.json())

            return response_200
        return response

    def get_known_users(
        self,
    ) -> UsersStats:
        """Get user IDs of known users

        Get the list of user IDs of users with any direct relationship with a
        user. That means any user sharing any channel, including direct and
        group channels.

        Permissions:
            Must be authenticated.
        Minimum Server Version:
            5.23
        """

        url = "/users/known".format()

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
            response_200 = UsersStats.parse_obj(response.json())

            return response_200
        return response

    def get_total_users_stats(
        self,
    ) -> UsersStats:
        """Get total count of users in the system

        Get a total count of users in the system.

        Permissions:
            Must be authenticated.
        """

        url = "/users/stats".format()

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
            response_200 = UsersStats.parse_obj(response.json())

            return response_200
        return response

    def get_total_users_stats_filtered(
        self,
        *,
        in_team: Optional[str] = None,
        in_channel: Optional[str] = None,
        include_deleted: Optional[bool] = None,
        include_bots: Optional[bool] = None,
        roles: Optional[str] = None,
        channel_roles: Optional[str] = None,
        team_roles: Optional[str] = None,
    ) -> UsersStats:
        """Get total count of users in the system matching the specified filters

        Get a count of users in the system matching the specified filters.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.26
        """

        url = "/users/stats/filtered".format()
        params: Dict[str, Any] = {
            "in_team": in_team,
            "in_channel": in_channel,
            "include_deleted": include_deleted,
            "include_bots": include_bots,
            "roles": roles,
            "channel_roles": channel_roles,
            "team_roles": team_roles,
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
            response_200 = UsersStats.parse_obj(response.json())

            return response_200
        return response

    def get_user(
        self,
        user_id: str,
    ) -> User:
        """Get a user

        Get a user a object. Sensitive information will be sanitized out.

        Permissions:
            Requires an active session but no other permissions.
        """

        url = "/users/{user_id}".format(
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
            response_200 = User.parse_obj(response.json())

            return response_200
        return response

    def update_user(
        self,
        user_id: str,
        *,
        json_body: UpdateUserJsonBody,
    ) -> User:
        """Update a user

        Update a user by providing the user object. The fields that can be
        updated are defined in the request body, all other provided fields will
        be ignored. Any fields not included in the request body will be set to
        null or reverted to default values.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}".format(
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
            response_200 = User.parse_obj(response.json())

            return response_200
        return response

    def delete_user(
        self,
        user_id: str,
    ) -> StatusOK:
        """Deactivate a user account.

        Deactivates the user and revokes all its sessions by archiving its user
        object.

        As of server version 5.28, optionally use the `permanent=true` query
        parameter to permanently delete the user for compliance reasons. To use
        this feature `ServiceSettings.EnableAPIUserDeletion` must be set to
        `true` in the server's configuration.

        Permissions:
            Must be logged in as the user being deactivated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}".format(
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

    def patch_user(
        self,
        user_id: str,
        *,
        json_body: PatchUserJsonBody,
    ) -> User:
        """Patch a user

        Partially update a user by providing only the fields you want to update.
        Omitted fields will not be updated. The fields that can be updated are
        defined in the request body, all other provided fields will be ignored.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/patch".format(
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
            response_200 = User.parse_obj(response.json())

            return response_200
        return response

    def update_user_roles(
        self,
        user_id: str,
        *,
        json_body: UpdateUserRolesJsonBody,
    ) -> StatusOK:
        """Update a user's roles

        Update a user's system-level roles. Valid user roles are
        \"system_user\", \"system_admin\" or both of them. Overwrites any
        previously assigned system-level roles.

        Permissions:
            Must have the `manage_roles` permission.
        """

        url = "/users/{user_id}/roles".format(
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

    def update_user_active(
        self,
        user_id: str,
        *,
        json_body: UpdateUserActiveJsonBody,
    ) -> StatusOK:
        """Update user active status

        Update user active or inactive status.

        __Since server version 4.6, users using a SSO provider to login can be
        activated or deactivated with this endpoint. However, if their
        activation status in Mattermost does not reflect their status in the SSO
        provider, the next synchronization or login by that user will reset the
        activation status to that of their account in the SSO provider. Server
        versions 4.5 and before do not allow activation or deactivation of SSO
        users from this endpoint.__
        User with `manage_system` permission can activate or deactivate a user.

        Permissions:
            User can deactivate themselves.
        """

        url = "/users/{user_id}/active".format(
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

    def get_profile_image(
        self,
        user_id: str,
    ) -> None:
        """Get user's profile image

        Get a user's profile image based on user_id string parameter.

        Permissions:
            Must be logged in.
        """

        url = "/users/{user_id}/image".format(
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

        return response

    def set_profile_image(
        self,
        user_id: str,
        *,
        multipart_data: SetProfileImageMultipartData,
    ) -> StatusOK:
        """Set user's profile image

        Set a user's profile image based on user_id string parameter.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/image".format(
            user_id=user_id,
        )

        multipart_body_data = SetProfileImageMultipartData.parse_obj(multipart_data)

        request_kwargs = {
            "url": url,
            "data": multipart_body_data.get_data(),
            "files": multipart_body_data.get_files(),
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def set_default_profile_image(
        self,
        user_id: str,
    ) -> StatusOK:
        """Delete user's profile image

        Delete user's profile image and reset to default image based on user_id
        string parameter.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        Minimum Server Version:
            5.5
        """

        url = "/users/{user_id}/image".format(
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

    def get_default_profile_image(
        self,
        user_id: str,
    ) -> None:
        """Return user's default (generated) profile image

        Returns the default (generated) user profile image based on user_id
        string parameter.

        Permissions:
            Must be logged in.
        Minimum Server Version:
            5.5
        """

        url = "/users/{user_id}/image/default".format(
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

        return response

    def get_user_by_username(
        self,
        username: str,
    ) -> User:
        """Get a user by username

        Get a user object by providing a username. Sensitive information will be
        sanitized out.

        Permissions:
            Requires an active session but no other permissions.
        """

        url = "/users/username/{username}".format(
            username=username,
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
            response_200 = User.parse_obj(response.json())

            return response_200
        return response

    def reset_password(
        self,
        *,
        json_body: ResetPasswordJsonBody,
    ) -> StatusOK:
        """Reset password

        Update the password for a user using a one-use, timed recovery code tied
        to the user's account. Only works for non-SSO users.

        Permissions:
            No permissions required.
        """

        url = "/users/password/reset".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def update_user_mfa(
        self,
        user_id: str,
        *,
        json_body: UpdateUserMfaJsonBody,
    ) -> StatusOK:
        """Update a user's MFA

        Activates multi-factor authentication for the user if `activate` is true
        and a valid `code` is provided. If activate is false, then `code` is not
        required and multi-factor authentication is disabled for the user.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/mfa".format(
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

    def generate_mfa_secret(
        self,
        user_id: str,
    ) -> GenerateMfaSecretResponse_200:
        """Generate MFA secret

        Generates an multi-factor authentication secret for a user and returns
        it as a string and as base64 encoded QR code image.

        Permissions:
            Must be logged in as the user or have the `edit_other_users`
        permission.
        """

        url = "/users/{user_id}/mfa/generate".format(
            user_id=user_id,
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
            response_200 = GenerateMfaSecretResponse_200.parse_obj(response.json())

            return response_200
        return response

    def demote_user_to_guest(
        self,
        user_id: str,
    ) -> StatusOK:
        """Demote a user to a guest

        Convert a regular user into a guest. This will convert the user into a
        guest for the whole system while retaining their existing team and
        channel memberships.

        Permissions:
            Must be logged in as the user or have the `demote_to_guest`
        permission.
        Minimum Server Version:
            5.16
        """

        url = "/users/{user_id}/demote".format(
            user_id=user_id,
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def promote_guest_to_user(
        self,
        user_id: str,
    ) -> StatusOK:
        """Promote a guest to user

        Convert a guest into a regular user. This will convert the guest into a
        user for the whole system while retaining any team and channel
        memberships and automatically joining them to the default channels.

        Permissions:
            Must be logged in as the user or have the `promote_guest`
        permission.
        Minimum Server Version:
            5.16
        """

        url = "/users/{user_id}/promote".format(
            user_id=user_id,
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def convert_user_to_bot(
        self,
        user_id: str,
    ) -> StatusOK:
        """Convert a user into a bot

        Convert a user into a bot.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.26
        """

        url = "/users/{user_id}/convert_to_bot".format(
            user_id=user_id,
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def check_user_mfa(
        self,
        *,
        json_body: CheckUserMfaJsonBody,
    ) -> CheckUserMfaResponse_200:
        """Check MFA

        Check if a user has multi-factor authentication active on their account
        by providing a login id. Used to check whether an MFA code needs to be
        provided when logging in.

        Permissions:
            No permission required.
        """

        url = "/users/mfa".format()

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
            response_200 = CheckUserMfaResponse_200.parse_obj(response.json())

            return response_200
        return response

    def update_user_password(
        self,
        user_id: str,
        *,
        json_body: UpdateUserPasswordJsonBody,
    ) -> StatusOK:
        """Update a user's password

        Update a user's password. New password must meet password policy set by
        server configuration. Current password is required if you're updating
        your own password.

        Permissions:
            Must be logged in as the user the password is being changed for or
        have `manage_system` permission.
        """

        url = "/users/{user_id}/password".format(
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

    def send_password_reset_email(
        self,
        *,
        json_body: SendPasswordResetEmailJsonBody,
    ) -> StatusOK:
        """Send password reset email

        Send an email containing a link for resetting the user's password. The
        link will contain a one-use, timed recovery code tied to the user's
        account. Only works for non-SSO users.

        Permissions:
            No permissions required.
        """

        url = "/users/password/reset/send".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def get_user_by_email(
        self,
        email: str,
    ) -> User:
        """Get a user by email

        Get a user object by providing a user email. Sensitive information will
        be sanitized out.

        Permissions:
            Requires an active session and for the current session to be able to
        view another user's email based on the server's privacy settings.
        """

        url = "/users/email/{email}".format(
            email=email,
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
            response_200 = User.parse_obj(response.json())

            return response_200
        return response

    def get_sessions(
        self,
        user_id: str,
    ) -> List[Session]:
        """Get user's sessions

        Get a list of sessions by providing the user GUID. Sensitive information
        will be sanitized out.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/sessions".format(
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
                response_200_item = Session.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def revoke_session(
        self,
        user_id: str,
        *,
        json_body: RevokeSessionJsonBody,
    ) -> StatusOK:
        """Revoke a user session

        Revokes a user session from the provided user id and session id strings.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/sessions/revoke".format(
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def revoke_all_sessions(
        self,
        user_id: str,
    ) -> StatusOK:
        """Revoke all active sessions for a user

        Revokes all user sessions from the provided user id and session id
        strings.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        Minimum Server Version:
            4.4
        """

        url = "/users/{user_id}/sessions/revoke/all".format(
            user_id=user_id,
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def attach_device_id(
        self,
        *,
        json_body: AttachDeviceIdJsonBody,
    ) -> StatusOK:
        """Attach mobile device

        Attach a mobile device id to the currently logged in session. This will
        enable push notifications for a user, if configured by the server.

        Permissions:
            Must be authenticated.
        """

        url = "/users/sessions/device".format()

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

    def get_user_audits(
        self,
        user_id: str,
    ) -> List[Audit]:
        """Get user's audits

        Get a list of audit by providing the user GUID.

        Permissions:
            Must be logged in as the user or have the `edit_other_users`
        permission.
        """

        url = "/users/{user_id}/audits".format(
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
                response_200_item = Audit.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def verify_user_email_without_token(
        self,
        user_id: str,
    ) -> User:
        """Verify user email by ID

        Verify the email used by a user without a token.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.24
        """

        url = "/users/{user_id}/email/verify/member".format(
            user_id=user_id,
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
            response_200 = User.parse_obj(response.json())

            return response_200
        return response

    def verify_user_email(
        self,
        *,
        json_body: VerifyUserEmailJsonBody,
    ) -> StatusOK:
        """Verify user email

        Verify the email used by a user to sign-up their account with.

        Permissions:
            No permissions required.
        """

        url = "/users/email/verify".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def send_verification_email(
        self,
        *,
        json_body: SendVerificationEmailJsonBody,
    ) -> StatusOK:
        """Send verification email

        Send an email with a verification link to a user that has an email
        matching the one in the request body. This endpoint will return success
        even if the email does not match any users on the system.

        Permissions:
            No permissions required.
        """

        url = "/users/email/verify/send".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def switch_account_type(
        self,
        *,
        json_body: SwitchAccountTypeJsonBody,
    ) -> SwitchAccountTypeResponse_200:
        """Switch login method

        Switch a user's login method from using email to OAuth2/SAML/LDAP or
        back to email. When switching to OAuth2/SAML, account switching is not
        complete until the user follows the returned link and completes any
        steps on the OAuth2/SAML service provider.

        To switch from email to OAuth2/SAML, specify `current_service`,
        `new_service`, `email` and `password`.

        To switch from OAuth2/SAML to email, specify `current_service`,
        `new_service`, `email` and `new_password`.

        To switch from email to LDAP/AD, specify `current_service`,
        `new_service`, `email`, `password`, `ldap_ip` and `new_password` (this
        is the user's LDAP password).

        To switch from LDAP/AD to email, specify `current_service`,
        `new_service`, `ldap_ip`, `password` (this is the user's LDAP password),
        `email`  and `new_password`.

        Additionally, specify `mfa_code` when trying to switch an account on
        LDAP/AD or email that has MFA activated.

        Permissions:
            No current authentication required except when switching from
        OAuth2/SAML to email.
        """

        url = "/users/login/switch".format()

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
            response_200 = SwitchAccountTypeResponse_200.parse_obj(response.json())

            return response_200
        return response

    def get_user_access_tokens_for_user(
        self,
        user_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[UserAccessTokenSanitized]:
        """Get user access tokens

        Get a list of user access tokens for a user. Does not include the actual
        authentication tokens. Use query parameters for paging.

        Permissions:
            Must have `read_user_access_token` permission. For non-self
        requests, must also have the `edit_other_users` permission.
        Minimum Server Version:
            4.1
        """

        url = "/users/{user_id}/tokens".format(
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
                response_200_item = UserAccessTokenSanitized.parse_obj(
                    response_200_item_data
                )

                response_200.append(response_200_item)

            return response_200
        return response

    def create_user_access_token(
        self,
        user_id: str,
        *,
        json_body: CreateUserAccessTokenJsonBody,
    ) -> UserAccessToken:
        """Create a user access token

        Generate a user access token that can be used to authenticate with the
        Mattermost REST API.

        Permissions:
            Must have `create_user_access_token` permission. For non-self
        requests, must also have the `edit_other_users` permission.
        Minimum Server Version:
            4.1
        """

        url = "/users/{user_id}/tokens".format(
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

        if response.status_code == 201:
            response_201 = UserAccessToken.parse_obj(response.json())

            return response_201
        return response

    def get_user_access_tokens(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[UserAccessTokenSanitized]:
        """Get user access tokens

        Get a page of user access tokens for users on the system. Does not
        include the actual authentication tokens. Use query parameters for
        paging.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.7
        """

        url = "/users/tokens".format()
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
                response_200_item = UserAccessTokenSanitized.parse_obj(
                    response_200_item_data
                )

                response_200.append(response_200_item)

            return response_200
        return response

    def revoke_user_access_token(
        self,
        *,
        json_body: RevokeUserAccessTokenJsonBody,
    ) -> StatusOK:
        """Revoke a user access token

        Revoke a user access token and delete any sessions using the token.

        Permissions:
            Must have `revoke_user_access_token` permission. For non-self
        requests, must also have the `edit_other_users` permission.
        Minimum Server Version:
            4.1
        """

        url = "/users/tokens/revoke".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def get_user_access_token(
        self,
        token_id: str,
    ) -> UserAccessTokenSanitized:
        """Get a user access token

        Get a user access token. Does not include the actual authentication
        token.

        Permissions:
            Must have `read_user_access_token` permission. For non-self
        requests, must also have the `edit_other_users` permission.
        Minimum Server Version:
            4.1
        """

        url = "/users/tokens/{token_id}".format(
            token_id=token_id,
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
            response_200 = UserAccessTokenSanitized.parse_obj(response.json())

            return response_200
        return response

    def disable_user_access_token(
        self,
        *,
        json_body: DisableUserAccessTokenJsonBody,
    ) -> StatusOK:
        """Disable personal access token

        Disable a personal access token and delete any sessions using the token.
        The token can be re-enabled using `/users/tokens/enable`.

        Permissions:
            Must have `revoke_user_access_token` permission. For non-self
        requests, must also have the `edit_other_users` permission.
        Minimum Server Version:
            4.4
        """

        url = "/users/tokens/disable".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def enable_user_access_token(
        self,
        *,
        json_body: EnableUserAccessTokenJsonBody,
    ) -> StatusOK:
        """Enable personal access token

        Re-enable a personal access token that has been disabled.

        Permissions:
            Must have `create_user_access_token` permission. For non-self
        requests, must also have the `edit_other_users` permission.
        Minimum Server Version:
            4.4
        """

        url = "/users/tokens/enable".format()

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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def search_user_access_tokens(
        self,
        *,
        json_body: SearchUserAccessTokensJsonBody,
    ) -> List[UserAccessTokenSanitized]:
        """Search tokens

        Get a list of tokens based on search criteria provided in the request
        body. Searches are done against the token id, user id and username.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            4.7
        """

        url = "/users/tokens/search".format()

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
                response_200_item = UserAccessTokenSanitized.parse_obj(
                    response_200_item_data
                )

                response_200.append(response_200_item)

            return response_200
        return response

    def update_user_auth(
        self,
        user_id: str,
        *,
        json_body: UserAuthData,
    ) -> UserAuthData:
        """Update a user's authentication method

        Updates a user's authentication method. This can be used to change them
        to/from LDAP authentication for example.

        Permissions:
            Must have the `edit_other_users` permission.
        Minimum Server Version:
            4.6
        """

        url = "/users/{user_id}/auth".format(
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
            response_200 = UserAuthData.parse_obj(response.json())

            return response_200
        return response

    def get_user_terms_of_service(
        self,
        user_id: str,
    ) -> Union[AppError, UserTermsOfService]:
        """Fetches user's latest terms of service action if the latest action was
        for acceptance.

        Will be deprecated in v6.0
        Fetches user's latest terms of service action if the latest action was
        for acceptance.

        Permissions:
            Must be logged in as the user being acted on.
        Minimum Server Version:
            5.6
        """

        url = "/users/{user_id}/terms_of_service".format(
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
            response_200 = UserTermsOfService.parse_obj(response.json())

            return response_200
        if response.status_code == 404:
            response_404 = AppError.parse_obj(response.json())

            return response_404
        return response

    def register_terms_of_service_action(
        self,
        user_id: str,
        *,
        json_body: RegisterTermsOfServiceActionJsonBody,
    ) -> StatusOK:
        """Records user action when they accept or decline custom terms of service

        Records user action when they accept or decline custom terms of service.
        Records the action in audit table.
        Updates user's last accepted terms of service ID if they accepted it.

        Permissions:
            Must be logged in as the user being acted on.
        Minimum Server Version:
            5.4
        """

        url = "/users/{user_id}/terms_of_service".format(
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def revoke_sessions_from_all_users(
        self,
    ) -> None:
        """Revoke all sessions from all users.

        For any session currently on the server (including admin) it will be
        revoked.
        Clients will be notified to log out users.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.14
        """

        url = "/users/sessions/revoke/all".format()

        request_kwargs = {
            "url": url,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        return response

    def publish_user_typing(
        self,
        user_id: str,
        *,
        json_body: PublishUserTypingJsonBody,
    ) -> None:
        """Publish a user typing websocket event.

        Notify users in the given channel via websocket that the given user is
        typing.

        Permissions:
            Must have `manage_system` permission to publish for any user other
        than oneself.
        Minimum Server Version:
            5.26
        """

        url = "/users/{user_id}/typing".format(
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

        return response

    def get_uploads_for_user(
        self,
        user_id: str,
    ) -> List[UploadSession]:
        """Get uploads for a user

        Gets all the upload sessions belonging to a user.

        Permissions:
            Must be logged in as the user who created the upload sessions.
        Minimum Server Version:
            5.28
        """

        url = "/users/{user_id}/uploads".format(
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
                response_200_item = UploadSession.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_channel_members_with_team_data_for_user(
        self,
        user_id: str,
        *,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[ChannelMemberWithTeamData]:
        """Get all channel members from all teams for a user

        Get all channel members from all teams for a user.

        Permissions:
            Logged in as the user, or have `edit_other_users` permission.
        Minimum Server Version:
            6.2.0
        """

        url = "/users/{user_id}/channel_members".format(
            user_id=user_id,
        )
        params: Dict[str, Any] = {
            "page": page,
            "pageSize": page_size,
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
                response_200_item = ChannelMemberWithTeamData.parse_obj(
                    response_200_item_data
                )

                response_200.append(response_200_item)

            return response_200
        return response

    def migrate_auth_to_ldap(
        self,
        *,
        json_body: MigrateAuthToLdapJsonBody,
    ) -> None:
        """Migrate user accounts authentication type to LDAP.

        Migrates accounts from one authentication provider to another. For
        example, you can upgrade your authentication provider from email to
        LDAP.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.28
        """

        url = "/users/migrate_auth/ldap".format()

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

        return response

    def migrate_auth_to_saml(
        self,
        *,
        json_body: MigrateAuthToSamlJsonBody,
    ) -> None:
        """Migrate user accounts authentication type to SAML.

        Migrates accounts from one authentication provider to another. For
        example, you can upgrade your authentication provider from email to
        SAML.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.28
        """

        url = "/users/migrate_auth/saml".format()

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

        return response

    def convert_bot_to_user(
        self,
        bot_user_id: str,
        *,
        json_body: ConvertBotToUserJsonBody,
        set_system_admin: Optional[bool] = False,
    ) -> StatusOK:
        """Convert a bot into a user

        Convert a bot into a user.

        Permissions:
            Must have `manage_system` permission.
        Minimum Server Version:
            5.26
        """

        url = "/bots/{bot_user_id}/convert_to_user".format(
            bot_user_id=bot_user_id,
        )
        params: Dict[str, Any] = {
            "set_system_admin": set_system_admin,
        }
        params = {k: v for k, v in params.items() if v is not None}

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "json": json_json_body,
            "params": params,
        }

        with self.client._get_httpx_client() as httpx_client:
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response
