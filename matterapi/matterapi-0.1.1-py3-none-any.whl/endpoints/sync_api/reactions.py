from typing import Any, Dict, List

from pydantic import BaseModel

from ...models import PostIdToReactionsMap, Reaction, StatusOK
from ..base import ApiBaseClass


class ReactionsApi(ApiBaseClass):
    """Endpoints for creating, getting and removing emoji reactions."""

    def save_reaction(
        self,
        *,
        json_body: Reaction,
    ) -> Reaction:
        """Create a reaction

        Create a reaction.

        Permissions:
            Must have `read_channel` permission for the channel the post is in.
        """

        url = "{}/reactions".format(self.client.base_url)
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

        response = self.client.post(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = Reaction.parse_obj(response.json())

            return response_201
        return response

    def get_reactions(
        self,
        post_id: str,
    ) -> List[Reaction]:
        """Get a list of reactions to a post

        Get a list of reactions made by all users to a given post.

        Permissions:
            Must have `read_channel` permission for the channel the post is in.
        """

        url = "{}/posts/{post_id}/reactions".format(
            self.client.base_url, post_id=post_id
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
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = Reaction.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def delete_reaction(
        self,
        user_id: str,
        post_id: str,
        emoji_name: str,
    ) -> StatusOK:
        """Remove a reaction from a post

        Deletes a reaction made by a user from the given post.

        Permissions:
            Must be user or have `manage_system` permission.
        """

        url = "{}/users/{user_id}/posts/{post_id}/reactions/{emoji_name}".format(
            self.client.base_url,
            user_id=user_id,
            post_id=post_id,
            emoji_name=emoji_name,
        )
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = self.client.delete(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    def get_bulk_reactions(
        self,
        *,
        json_body: List[str],
    ) -> PostIdToReactionsMap:
        """Bulk get the reaction for posts

        Get a list of reactions made by all users to a given post.

        Permissions:
            Must have `read_channel` permission for the channel the post is in.
        Minimum Server Version:
            5.8
        """

        url = "{}/posts/ids/reactions".format(self.client.base_url)
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
            response_200 = PostIdToReactionsMap.parse_obj(response.json())

            return response_200
        return response
