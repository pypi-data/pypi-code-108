from valohai_cli.api import request

from jupyhai import consts
from jupyhai.api_urls import LOGIN_LINK_URL
from jupyhai.handlers.base import JupyhaiHandler
from jupyhai.utils.executions import get_execution_by_id


class ExecutionUrlWithTokenHandler(JupyhaiHandler):
    def get(self, execution_id: str) -> None:
        self.finish({'url': self.get_execution_url(execution_id)})

    def get_execution_url(self, executionid: str) -> str:
        execution = get_execution_by_id(executionid)
        assert execution

        response = request('get', LOGIN_LINK_URL)
        result = response.json()
        if not result:
            raise RuntimeError("Unable to login")

        return "%(host)s%(login_url)s&next=%(redirect_url)s" % {
            "host": consts.HOST,
            "login_url": result['url'],
            "redirect_url": execution['urls']['display'],
        }
