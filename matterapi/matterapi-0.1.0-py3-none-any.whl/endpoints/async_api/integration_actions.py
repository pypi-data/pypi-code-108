from typing import Any, Dict

from pydantic import BaseModel

from ...models import (
    OpenInteractiveDialogJsonBody,
    StatusOK,
    SubmitInteractiveDialogJsonBody,
)
from ..base import ApiBaseClass


class IntegrationActionsApi(ApiBaseClass):
    """Endpoints for interactive actions for use by integrations."""

    async def open_interactive_dialog(
        self,
        *,
        json_body: OpenInteractiveDialogJsonBody,
    ) -> StatusOK:
        """Open a dialog

        Open an interactive dialog using a trigger ID provided by a slash
        command, or some other action payload. See
        https://docs.mattermost.com/developer/interactive-dialogs.html for more
        information on interactive dialogs.

        Minimum Server Version:
            5.6
        """

        url = "{}/actions/dialogs/open".format(self.client.base_url)
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

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response

    async def submit_interactive_dialog(
        self,
        *,
        json_body: SubmitInteractiveDialogJsonBody,
    ) -> StatusOK:
        """Submit a dialog

        Endpoint used by the Mattermost clients to submit a dialog. See
        https://docs.mattermost.com/developer/interactive-dialogs.html for more
        information on interactive dialogs.

        Minimum Server Version:
            5.6
        """

        url = "{}/actions/dialogs/submit".format(self.client.base_url)
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

        if response.status_code == 200:
            response_200 = StatusOK.parse_obj(response.json())

            return response_200
        return response
