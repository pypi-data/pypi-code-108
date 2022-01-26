from typing import List

from pydantic import BaseModel

from ...models import Preference, StatusOK
from ..base import ApiBaseClass


class PreferencesApi(ApiBaseClass):
    """Endpoints for saving and modifying user preferences."""

    def get_preferences(
        self,
        user_id: str,
    ) -> List[Preference]:
        """Get the user's preferences

        Get a list of the user's preferences.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/preferences".format(
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
                response_200_item = Preference.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def update_preferences(
        self,
        user_id: str,
        *,
        json_body: List[Preference],
    ) -> StatusOK:
        """Save the user's preferences

        Save a list of the user's preferences.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/preferences".format(
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
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def delete_preferences(
        self,
        user_id: str,
        *,
        json_body: List[Preference],
    ) -> StatusOK:
        """Delete user's preferences

        Delete a list of the user's preferences.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/preferences/delete".format(
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
            response = httpx_client.post(
                **request_kwargs,
            )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def get_preferences_by_category(
        self,
        user_id: str,
        category: str,
    ) -> List[Preference]:
        """List a user's preferences by category

        Lists the current user's stored preferences in the given category.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/preferences/{category}".format(
            user_id=user_id,
            category=category,
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
                response_200_item = Preference.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def get_preferences_by_category_by_name(
        self,
        user_id: str,
        category: str,
        preference_name: str,
    ) -> Preference:
        """Get a specific user preference

        Gets a single preference for the current user with the given category
        and name.

        Permissions:
            Must be logged in as the user being updated or have the
        `edit_other_users` permission.
        """

        url = "/users/{user_id}/preferences/{category}/name/{preference_name}".format(
            user_id=user_id,
            category=category,
            preference_name=preference_name,
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
            response_200 = Preference.parse_obj(response.json())

            return response_200
        return response
