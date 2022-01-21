from typing import Iterable, List, Optional

from valohai_cli.api import request
from valohai_cli.ctx import set_project_link
from valohai_cli.exceptions import APINotFoundError
from valohai_cli.settings import settings
from valohai_yaml.objs import Mount

from jupyhai import consts
from jupyhai.api_urls import PROJECTS_URL
from jupyhai.handlers.base import JupyhaiHandler
from jupyhai.utils import (
    get_current_environment,
    get_current_host_is_minihai,
    get_current_ignore,
    get_current_image,
    get_current_mounts,
    get_current_project,
    get_current_title,
)
from jupyhai.utils.auth import login_status


class SettingsHandler(JupyhaiHandler):
    def get(self) -> None:
        project = get_current_project()
        result = {
            'project': getattr(project, 'id', None) or '',
            'environment': get_current_environment(),
            'image': get_current_image(),
            'title': get_current_title(),
            'ignore': get_current_ignore(),
            'mounts': [mount.serialize() for mount in get_current_mounts()],
            'hostIsMinihai': get_current_host_is_minihai(),
        }
        self.finish({'result': result})

    def post(self) -> None:
        args = self.get_json_body()
        self.set_jupyhai_settings(
            project_id=args['project_id'],
            environment=args.get('environment_id'),
            image=args['image'],
            title=args['title'],
            ignore=list(args['ignore']),
            mounts=_validate_mounts(args['mounts']),
            host_is_minihai=bool(args.get('host_is_minihai')),
        )
        self.finish({'success': True})

    def set_jupyhai_settings(
        self,
        *,
        project_id: Optional[str],
        environment: Optional[str],
        image: str,
        title: Optional[str],
        ignore: List[str],
        mounts: List[dict],
        host_is_minihai: bool,
    ) -> None:
        project = get_current_project()
        logged_in = login_status()
        if logged_in and (getattr(project, 'id', None) != project_id) and project_id:
            self.link_project(project_id)
        settings.persistence.update(
            jupyhai_image=image,
            jupyhai_environment=environment,
            jupyhai_title=title,
            jupyhai_ignore=ignore,
            jupyhai_mounts=mounts,
            jupyhai_host_is_minihai=host_is_minihai,
        )
        settings.persistence.save()

    def link_project(self, id: str) -> None:
        try:
            response = request('get', '%s%s/' % (PROJECTS_URL, id))
            responseJSON = response.json()
        except APINotFoundError:
            self.log.error('No Project %s found.' % id)
            return

        os_path = consts.ROOT_DIRECTORY
        if responseJSON:
            set_project_link(os_path, responseJSON)
        else:
            self.log.info(responseJSON)
            self.log.info("Error in linking project %s" % (id))


def _validate_mounts(mounts: Iterable[dict]) -> List[dict]:
    return [Mount.parse(data).serialize() for data in mounts]
