from typing import List, Optional

from valohai_cli.api import request

from jupyhai.api_urls import ENVIRONMENTS_URL
from jupyhai.handlers.base import JupyhaiHandler
from jupyhai.utils import filter_environments, get_current_environment


class EnvironmentsHandler(JupyhaiHandler):
    def get(self, tag: Optional[str] = None) -> None:
        if tag == "current":
            self.finish({'id': get_current_environment()})
        else:
            self.finish({'results': self.get_environments()})

    def get_environments(self) -> List[dict]:
        response = request('get', ENVIRONMENTS_URL, params={'limit': 9999})
        responseJSON = response.json()

        if not responseJSON or not responseJSON['results']:
            self.log.error('No Environments.')
            return []

        return filter_environments(responseJSON['results'])
