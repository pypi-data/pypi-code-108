from typing import Any, Dict

from ...models import StatusOK
from ..base import ApiBaseClass


class BleveApi(ApiBaseClass):
    """ """

    async def purge_bleve_indexes(
        self,
    ) -> StatusOK:
        """Purge all Bleve indexes

        Deletes all Bleve indexes and their contents. After calling this
        endpoint, it is
        necessary to schedule a new Bleve indexing job to repopulate the
        indexes.

        Permissions:
            Must have `sysconsole_write_experimental` permission.
        Minimum Server Version:
            5.24
        """

        url = "{}/bleve/purge_indexes".format(self.client.base_url)
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
