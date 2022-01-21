from typing import Iterable, List, Optional

from notebook.notebookapp import list_running_servers
from valohai_cli.ctx import get_project
from valohai_cli.models.project import Project
from valohai_cli.settings import settings
from valohai_yaml.objs import Mount

from jupyhai import consts
from jupyhai.consts import DEFAULT_IGNORE, DEFAULT_IMAGE, DEFAULT_TITLE


def filter_environments(environments: Iterable[dict]) -> List[dict]:
    return [env for env in environments if env['enabled']]


def get_current_project() -> Optional[Project]:
    return get_project(consts.ROOT_DIRECTORY)


def get_current_image() -> str:
    return str(settings.persistence.get('jupyhai_image', DEFAULT_IMAGE))


def get_current_environment() -> Optional[str]:
    env = settings.persistence.get('jupyhai_environment')
    if env:
        return str(env)
    return None


def get_current_title() -> str:
    return str(settings.persistence.get('jupyhai_title', DEFAULT_TITLE))


def get_current_ignore() -> List[str]:
    return list(settings.persistence.get('jupyhai_ignore') or DEFAULT_IGNORE)


def get_current_mounts() -> List[Mount]:
    mounts = settings.persistence.get('jupyhai_mounts', [])
    if not mounts:
        mounts = []
    return [Mount.parse(data) for data in mounts]


def get_current_host_is_minihai() -> bool:
    return bool(settings.persistence.get('jupyhai_host_is_minihai', False))


def get_notebook_server():
    return next(list_running_servers())
