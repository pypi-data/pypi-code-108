from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ...models import (
    CreateIncomingWebhookJsonBody,
    CreateOutgoingWebhookJsonBody,
    IncomingWebhook,
    OutgoingWebhook,
    StatusOK,
    UpdateIncomingWebhookJsonBody,
    UpdateOutgoingWebhookJsonBody,
)
from ..base import ApiBaseClass


class WebhooksApi(ApiBaseClass):
    """Endpoints for creating, getting and updating webhooks."""

    async def get_incoming_webhooks(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
        team_id: Optional[str] = None,
    ) -> List[IncomingWebhook]:
        """List incoming webhooks

        Get a page of a list of incoming webhooks. Optionally filter for a
        specific team using query parameters.

        Permissions:
            `manage_webhooks` for the system or `manage_webhooks` for the
        specific team.
        """

        url = "{}/hooks/incoming".format(self.client.base_url)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "team_id": team_id,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
            "params": params,
        }

        response = await self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = IncomingWebhook.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def create_incoming_webhook(
        self,
        *,
        json_body: CreateIncomingWebhookJsonBody,
    ) -> IncomingWebhook:
        """Create an incoming webhook

        Create an incoming webhook for a channel.

        `manage_others_incoming_webhooks` for the team the webhook is in if the
        user is different than the requester.

        Permissions:
            `manage_webhooks` for the team the webhook is in.
        """

        url = "{}/hooks/incoming".format(self.client.base_url)
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

        response = await self.client.post(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = IncomingWebhook.parse_obj(response.json())

            return response_201
        return response

    async def get_incoming_webhook(
        self,
        hook_id: str,
    ) -> IncomingWebhook:
        """Get an incoming webhook

        Get an incoming webhook given the hook id.

        Permissions:
            `manage_webhooks` for system or `manage_webhooks` for the specific
        team or `manage_webhooks` for the channel.
        """

        url = "{}/hooks/incoming/{hook_id}".format(
            self.client.base_url, hook_id=hook_id
        )
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = await self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = IncomingWebhook.parse_obj(response.json())

            return response_200
        return response

    async def update_incoming_webhook(
        self,
        hook_id: str,
        *,
        json_body: UpdateIncomingWebhookJsonBody,
    ) -> IncomingWebhook:
        """Update an incoming webhook

        Update an incoming webhook given the hook id.

        Permissions:
            `manage_webhooks` for system or `manage_webhooks` for the specific
        team or `manage_webhooks` for the channel.
        """

        url = "{}/hooks/incoming/{hook_id}".format(
            self.client.base_url, hook_id=hook_id
        )
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

        response = await self.client.put(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = IncomingWebhook.parse_obj(response.json())

            return response_200
        return response

    async def delete_incoming_webhook(
        self,
        hook_id: str,
    ) -> StatusOK:
        """Delete an incoming webhook

        Delete an incoming webhook given the hook id.

        Permissions:
            `manage_webhooks` for system or `manage_webhooks` for the specific
        team or `manage_webhooks` for the channel.
        """

        url = "{}/hooks/incoming/{hook_id}".format(
            self.client.base_url, hook_id=hook_id
        )
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = await self.client.delete(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def get_outgoing_webhooks(
        self,
        *,
        page: Optional[int] = 0,
        per_page: Optional[int] = 60,
        team_id: Optional[str] = None,
        channel_id: Optional[str] = None,
    ) -> List[OutgoingWebhook]:
        """List outgoing webhooks

        Get a page of a list of outgoing webhooks. Optionally filter for a
        specific team or channel using query parameters.

        Permissions:
            `manage_webhooks` for the system or `manage_webhooks` for the
        specific team/channel.
        """

        url = "{}/hooks/outgoing".format(self.client.base_url)
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()
        params: Dict[str, Any] = {
            "page": page,
            "per_page": per_page,
            "team_id": team_id,
            "channel_id": channel_id,
        }
        params = {k: v for k, v in params.items() if v is not None}

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
            "params": params,
        }

        response = await self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = []
            _response_200 = response.json()
            for response_200_item_data in _response_200:
                response_200_item = OutgoingWebhook.parse_obj(response_200_item_data)

                response_200.append(response_200_item)

            return response_200
        return response

    async def create_outgoing_webhook(
        self,
        *,
        json_body: CreateOutgoingWebhookJsonBody,
    ) -> OutgoingWebhook:
        """Create an outgoing webhook

        Create an outgoing webhook for a team.

        `manage_others_outgoing_webhooks` for the team the webhook is in if the
        user is different than the requester.

        Permissions:
            `manage_webhooks` for the team the webhook is in.
        """

        url = "{}/hooks/outgoing".format(self.client.base_url)
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

        response = await self.client.post(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 201:
            response_201 = OutgoingWebhook.parse_obj(response.json())

            return response_201
        return response

    async def get_outgoing_webhook(
        self,
        hook_id: str,
    ) -> OutgoingWebhook:
        """Get an outgoing webhook

        Get an outgoing webhook given the hook id.

        Permissions:
            `manage_webhooks` for system or `manage_webhooks` for the specific
        team or `manage_webhooks` for the channel.
        """

        url = "{}/hooks/outgoing/{hook_id}".format(
            self.client.base_url, hook_id=hook_id
        )
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = await self.client.get(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = OutgoingWebhook.parse_obj(response.json())

            return response_200
        return response

    async def update_outgoing_webhook(
        self,
        hook_id: str,
        *,
        json_body: UpdateOutgoingWebhookJsonBody,
    ) -> OutgoingWebhook:
        """Update an outgoing webhook

        Update an outgoing webhook given the hook id.

        Permissions:
            `manage_webhooks` for system or `manage_webhooks` for the specific
        team or `manage_webhooks` for the channel.
        """

        url = "{}/hooks/outgoing/{hook_id}".format(
            self.client.base_url, hook_id=hook_id
        )
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

        response = await self.client.put(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = OutgoingWebhook.parse_obj(response.json())

            return response_200
        return response

    async def delete_outgoing_webhook(
        self,
        hook_id: str,
    ) -> StatusOK:
        """Delete an outgoing webhook

        Delete an outgoing webhook given the hook id.

        Permissions:
            `manage_webhooks` for system or `manage_webhooks` for the specific
        team or `manage_webhooks` for the channel.
        """

        url = "{}/hooks/outgoing/{hook_id}".format(
            self.client.base_url, hook_id=hook_id
        )
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = await self.client.delete(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def regen_outgoing_hook_token(
        self,
        hook_id: str,
    ) -> StatusOK:
        """Regenerate the token for the outgoing webhook.

        Regenerate the token for the outgoing webhook.

        Permissions:
            `manage_webhooks` for system or `manage_webhooks` for the specific
        team or `manage_webhooks` for the channel.
        """

        url = "{}/hooks/outgoing/{hook_id}/regen_token".format(
            self.client.base_url, hook_id=hook_id
        )
        headers: Dict[str, Any] = self.client.get_headers()
        cookies: Dict[str, Any] = self.client.get_cookies()

        request_kwargs = {
            "url": url,
            "headers": headers,
            "cookies": cookies,
        }

        response = await self.client.post(
            **request_kwargs,
        )

        if self.skip_response_parsing:
            return response

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response
