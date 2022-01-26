from pydantic import BaseModel

from ...models import OpenGraph, OpenGraphJsonBody
from ..base import ApiBaseClass


class OpenGraphApi(ApiBaseClass):
    """Endpoint for getting Open Graph metadata."""

    def open_graph(
        self,
        *,
        json_body: OpenGraphJsonBody,
    ) -> OpenGraph:
        """Get open graph metadata for url

        Get Open Graph Metadata for a specif URL. Use the Open Graph protocol to
        get some generic metadata about a URL. Used for creating link previews.

        Permissions:
            No permission required but must be logged in.
        Minimum Server Version:
            3.10
        """

        url = "/opengraph".format()

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
            response_200 = OpenGraph.parse_obj(response.json())

            return response_200
        return response
