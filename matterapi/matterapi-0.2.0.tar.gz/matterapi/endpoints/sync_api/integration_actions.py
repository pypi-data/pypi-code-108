from pydantic import BaseModel

from ...models import (
    OpenInteractiveDialogJsonBody,
    StatusOK,
    SubmitInteractiveDialogJsonBody,
)
from ..base import ApiBaseClass


class IntegrationActionsApi(ApiBaseClass):
    """Endpoints for interactive actions for use by integrations."""

    def open_interactive_dialog(
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

        url = "/actions/dialogs/open".format()

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

    def submit_interactive_dialog(
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

        url = "/actions/dialogs/submit".format()

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
