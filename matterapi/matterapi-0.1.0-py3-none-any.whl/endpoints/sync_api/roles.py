from typing import Any, Dict, List

from pydantic import BaseModel

from ...models import PatchRoleJsonBody, Role
from ..base import ApiBaseClass


class RolesApi(ApiBaseClass):
    """Endpoints for creating, getting and updating roles."""

    def get_all_roles(
        self,
    ) -> List[Role]:
        """Get a list of all the roles



        Permissions:
            `manage_system` permission is required.
        Minimum Server Version:
            5.33
        """

        url = "{}/roles".format(self.client.base_url)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Role.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_role(
        self,
        role_id: str,
    ) -> Role:
        """Get a role

        Get a role from the provided role id.

        Permissions:
            Requires an active session but no other permissions.
        Minimum Server Version:
            4.9
        """

        url = "{}/roles/{role_id}".format(self.client.base_url, role_id=role_id)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Role.parse_obj(response.json())

            return response_200
        return response

    def get_role_by_name(
        self,
        role_name: str,
    ) -> Role:
        """Get a role

        Get a role from the provided role name.

        Permissions:
            Requires an active session but no other permissions.
        Minimum Server Version:
            4.9
        """

        url = "{}/roles/name/{role_name}".format(
            self.client.base_url, role_name=role_name
        )
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Role.parse_obj(response.json())

            return response_200
        return response

    def patch_role(
        self,
        role_id: str,
        *,
        json_body: PatchRoleJsonBody,
    ) -> Role:
        """Patch a role

        Partially update a role by providing only the fields you want to update.
        Omitted fields will not be updated. The fields that can be updated are
        defined in the request body, all other provided fields will be ignored.

        Permissions:
            `manage_system` permission is required.
        Minimum Server Version:
            4.9
        """

        url = "{}/roles/{role_id}/patch".format(self.client.base_url, role_id=role_id)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        if isinstance(json_body, BaseModel):
            json_json_body = json_body.dict(exclude_unset=True)
        else:
            json_json_body = json_body

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
            "json": json_json_body,
        }

        response = self.client.put(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = Role.parse_obj(response.json())

            return response_200
        return response

    def get_roles_by_names(
        self,
        *,
        json_body: List[str],
    ) -> List[Role]:
        """Get a list of roles by name

        Get a list of roles from their names.

        Permissions:
            Requires an active session but no other permissions.
        Minimum Server Version:
            4.9
        """

        url = "{}/roles/names".format(self.client.base_url)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()
        json_json_body = json_body

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
            "json": json_json_body,
        }

        response = self.client.post(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Role.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response
