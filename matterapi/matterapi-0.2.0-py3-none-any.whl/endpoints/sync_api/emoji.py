from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ...models import CreateEmojiMultipartData, Emoji, SearchEmojiJsonBody
from ..base import ApiBaseClass


class EmojiApi(ApiBaseClass):
    """Endpoints for creating, getting and interacting with emojis."""

    def get_emoji_list(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
        sort: Optional[str] = "",
    ) -> Emoji:
        """Get a list of custom emoji

        Get a page of metadata for custom emoji on the system. Since server
        version 4.7, sort using the `sort` query parameter.

        Permissions:
            Must be authenticated.
        """

        url = "/emoji".format()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "sort": sort,
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
            response_200 = Emoji.parse_obj(response.json())

            return response_200
        return response

    def create_emoji(
        self,
        *,
        multipart_data: CreateEmojiMultipartData,
    ) -> Emoji:
        """Create a custom emoji

        Create a custom emoji for the team.

        Permissions:
            Must be authenticated.
        """

        url = "/emoji".format()

        multipart_body_data = CreateEmojiMultipartData.parse_obj(multipart_data)

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

        if response.status_code == 201:
            response_201 = Emoji.parse_obj(response.json())

            return response_201
        return response

    def get_emoji(
        self,
        emoji_id: str,
    ) -> Emoji:
        """Get a custom emoji

        Get some metadata for a custom emoji.

        Permissions:
            Must be authenticated.
        """

        url = "/emoji/{emoji_id}".format(
            emoji_id=emoji_id,
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
            response_200 = Emoji.parse_obj(response.json())

            return response_200
        return response

    def delete_emoji(
        self,
        emoji_id: str,
    ) -> Emoji:
        """Delete a custom emoji

        Delete a custom emoji.

        Permissions:
            Must have the `manage_team` or `manage_system` permissions or be the
        user who created the emoji.
        """

        url = "/emoji/{emoji_id}".format(
            emoji_id=emoji_id,
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
            response_200 = Emoji.parse_obj(response.json())

            return response_200
        return response

    def get_emoji_by_name(
        self,
        emoji_name: str,
    ) -> Emoji:
        """Get a custom emoji by name

        Get some metadata for a custom emoji using its name.

        Permissions:
            Must be authenticated.
        Minimum Server Version:
            4.7
        """

        url = "/emoji/name/{emoji_name}".format(
            emoji_name=emoji_name,
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
            response_200 = Emoji.parse_obj(response.json())

            return response_200
        return response

    def get_emoji_image(
        self,
        emoji_id: str,
    ) -> None:
        """Get custom emoji image

        Get the image for a custom emoji.

        Permissions:
            Must be authenticated.
        """

        url = "/emoji/{emoji_id}/image".format(
            emoji_id=emoji_id,
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

    def search_emoji(
        self,
        *,
        json_body: SearchEmojiJsonBody,
    ) -> List[Emoji]:
        """Search custom emoji

        Search for custom emoji by name based on search criteria provided in the
        request body. A maximum of 200 results are returned.

        Permissions:
            Must be authenticated.
        Minimum Server Version:
            4.7
        """

        url = "/emoji/search".format()

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
                response_200_item = Emoji.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    def autocomplete_emoji(
        self,
        *,
        name: str,
    ) -> Emoji:
        """Autocomplete custom emoji

        Get a list of custom emoji with names starting with or matching the
        provided name. Returns a maximum of 100 results.

        Permissions:
            Must be authenticated.
        Minimum Server Version:
            4.7
        """

        url = "/emoji/autocomplete".format()
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
            response_200 = Emoji.parse_obj(response.json())

            return response_200
        return response
