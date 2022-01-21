from typing import Optional

from valohai_cli.api import request

from jupyhai.api_urls import PROJECTS_URL
from jupyhai.handlers.base import JupyhaiHandler
from jupyhai.utils import get_current_project


class ProjectsHandler(JupyhaiHandler):
    def get(self, tag: Optional[str] = None) -> None:
        if tag == "current":
            project = get_current_project()
            if project:
                self.finish(dict(project.data))  # cached JSON blob
                return
            else:
                self.finish({'id': None})
                return
        else:
            response = request('get', PROJECTS_URL, params={'limit': 9999})
            projects = response.json()['results']
            self.finish({'results': projects})
