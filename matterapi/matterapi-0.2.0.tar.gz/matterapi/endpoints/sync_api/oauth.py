from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ...models import CreateOAuthAppJsonBody, OAuthApp, StatusOK, UpdateOAuthAppJsonBody
from ..base import ApiBaseClass


class OauthApi(ApiBaseClass):
    """Endpoints for configuring and interacting with Mattermost as an OAuth
    2.0 service provider."""

    def get_oauth_apps(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[OAuthApp]:
        """Get OAuth apps

        Get a page of OAuth 2.0 client applications registered with Mattermost.

        Permissions:
            With `manage_oauth` permission, the apps registered by the logged in
        user are returned. With `manage_system_wide_oauth` permission, all apps
        regardless of creator are returned.
        """

        url = "/oauth/apps".format()
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
                response_200_item = OAuthApp.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def create_oauth_app(
        self,
        *,
        json_body: CreateOAuthAppJsonBody,
    ) -> OAuthApp:
        """Register OAuth app

        Register an OAuth 2.0 client application with Mattermost as the service
        provider.

        Permissions:
            Must have `manage_oauth` permission.
        """

        url = "/oauth/apps".format()

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
            response_201 = OAuthApp.parse_obj(response.json())

            return response_201
        return response

    def get_oauth_app(
        self,
        app_id: str,
    ) -> OAuthApp:
        """Get an OAuth app

        Get an OAuth 2.0 client application registered with Mattermost.

        Permissions:
            If app creator, must have `mange_oauth` permission otherwise
        `manage_system_wide_oauth` permission is required.
        """

        url = "/oauth/apps/{app_id}".format(
            app_id=app_id,
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
            response_200 = OAuthApp.parse_obj(response.json())

            return response_200
        return response

    def update_oauth_app(
        self,
        app_id: str,
        *,
        json_body: UpdateOAuthAppJsonBody,
    ) -> OAuthApp:
        """Update an OAuth app

        Update an OAuth 2.0 client application based on OAuth struct.

        Permissions:
            If app creator, must have `mange_oauth` permission otherwise
        `manage_system_wide_oauth` permission is required.
        """

        url = "/oauth/apps/{app_id}".format(
            app_id=app_id,
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
            response_200 = OAuthApp.parse_obj(response.json())

            return response_200
        return response

    def delete_oauth_app(
        self,
        app_id: str,
    ) -> StatusOK:
        """Delete an OAuth app

        Delete and unregister an OAuth 2.0 client application

        Permissions:
            If app creator, must have `mange_oauth` permission otherwise
        `manage_system_wide_oauth` permission is required.
        """

        url = "/oauth/apps/{app_id}".format(
            app_id=app_id,
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

    def regenerate_oauth_app_secret(
        self,
        app_id: str,
    ) -> OAuthApp:
        """Regenerate OAuth app secret

        Regenerate the client secret for an OAuth 2.0 client application
        registered with Mattermost.

        Permissions:
            If app creator, must have `mange_oauth` permission otherwise
        `manage_system_wide_oauth` permission is required.
        """

        url = "/oauth/apps/{app_id}/regen_secret".format(
            app_id=app_id,
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
            response_200 = OAuthApp.parse_obj(response.json())

            return response_200
        return response

    def get_oauth_app_info(
        self,
        app_id: str,
    ) -> OAuthApp:
        """Get info on an OAuth app

        Get public information about an OAuth 2.0 client application registered
        with Mattermost. The application's client secret will be blanked out.

        Permissions:
            Must be authenticated.
        """

        url = "/oauth/apps/{app_id}/info".format(
            app_id=app_id,
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
            response_200 = OAuthApp.parse_obj(response.json())

            return response_200
        return response

    def get_authorized_oauth_apps_for_user(
        self,
        user_id: str,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
    ) -> List[OAuthApp]:
        """Get authorized OAuth apps

        Get a page of OAuth 2.0 client applications authorized to access a
        user's account.

        Permissions:
            Must be authenticated as the user or have `edit_other_users`
        permission.
        """

        url = "/users/{user_id}/oauth/apps/authorized".format(
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
                response_200_item = OAuthApp.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response
