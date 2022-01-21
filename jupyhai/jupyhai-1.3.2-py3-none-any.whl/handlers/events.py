from typing import List, Optional
from urllib.parse import urljoin

import aiohttp
from valohai_cli.api import get_host_and_token

from jupyhai.handlers.base import JupyhaiHandler


class EventsHandler(JupyhaiHandler):
    async def get(self, execution_id: str) -> None:
        await self.finish({'results': await self.get_execution_events(execution_id)})

    async def get_execution_events(self, executionid: str) -> Optional[List[dict]]:
        host, token = get_host_and_token()
        headers = {'Authorization': 'Token %s' % token}
        url = urljoin(host, '/api/v0/executions/%s/events/') % executionid

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                responseJSON = await response.json()
                if not responseJSON or not responseJSON['events']:
                    return None

                return responseJSON['events']
