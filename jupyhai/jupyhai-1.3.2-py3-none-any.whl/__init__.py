# WARNING: This module may not import anything from within jupyhai
#          as it is being imported by `setup.py` – not all requirements
#          required are necessarily available during that import time.
import json
import os
from typing import TYPE_CHECKING, List

from ._version import __version__  # noqa

if TYPE_CHECKING:
    from notebook.notebookapp import NotebookApp


def _jupyter_server_extension_points() -> List[dict]:
    return [{"module": "jupyhai"}]


def _jupyter_labextension_paths():
    labextension_package_json_path = os.path.join(os.path.dirname(__file__), "labextension", "package.json")
    with open(labextension_package_json_path) as fid:
        data = json.load(fid)

    return [{
        "src": "labextension",
        "dest": data["name"],
    }]


def _jupyter_nbextension_paths() -> List[dict]:
    import pkg_resources

    jupyhai_js = pkg_resources.resource_filename('jupyhai', 'nbextension/jupyhai.js')
    if not os.path.isfile(jupyhai_js):
        raise RuntimeError(
            '%s is not a file – was the Jupyhai package built correctly?' % jupyhai_js
        )
    return [
        {
            'section': 'notebook',
            'src': jupyhai_js,
            'dest': 'jupyhai.js',
            'require': 'jupyhai',
        },
    ]


def _load_jupyter_server_extension(nb_server_app: 'NotebookApp') -> None:
    from .handlers.init import prepare

    prepare(nb_server_app)


# For backward compatibility with notebook server - useful for Binder/JupyterHub
load_jupyter_server_extension = _load_jupyter_server_extension
