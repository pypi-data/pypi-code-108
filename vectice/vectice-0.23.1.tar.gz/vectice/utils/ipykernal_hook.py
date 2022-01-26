import os
import json
import urllib.error
import urllib.request
import requests
from urllib.parse import unquote
from itertools import chain
from pathlib import Path, PurePath
from typing import Generator, Tuple, Union


FILE_ERROR = "Can't identify the notebook {}. When attempting to create auto code artifact."
CONN_ERROR = "Unable to access server;\n" + "ipynbname requires either no security or token based security."


class HttpError(Exception):
    def __init__(self, code: int, reason: str, path: str):
        super().__init__()
        self.code: int = code
        self.reason: str = reason
        self.path = path

    def __str__(self):
        return f"""HTTP Error Code {self.code} : {self.reason}
        {self.path}
        """


def _list_running_servers(runtime_dir=None) -> Generator[dict, None, None]:
    """Iterate over the server info files of running notebook servers."""
    from jupyter_core.paths import jupyter_runtime_dir

    if runtime_dir is None:
        runtime_dir = jupyter_runtime_dir()
    runtime_dir = Path(runtime_dir)

    if runtime_dir.is_dir():
        for file_name in chain(
            runtime_dir.glob("nbserver-*.json"),  # jupyter notebook (or lab 2)
            runtime_dir.glob("jpserver-*.json"),  # jupyterlab 3
        ):
            yield json.loads(file_name.read_bytes())


def _get_kernel_id() -> str:
    """Returns the kernel ID of the ipykernel."""
    import ipykernel

    connection_file = Path(ipykernel.get_connection_file()).stem
    kernel_id = connection_file.split("-", 1)[1]
    return kernel_id


def _get_sessions(server):
    """Given a server, returns sessions, or HTTPError if access is denied.
    NOTE: Works only when either there is no security or there is token
    based security. An HTTPError is raised if unable to connect to a
    server.
    """
    try:
        query_str = ""
        token = server["token"]
        if token:
            query_str = f"?token={token}"
        url = f"{server['url']}api/sessions{query_str}"  # nosec
        with urllib.request.urlopen(url) as request:  # nosec
            return json.load(request)  # nosec
    except Exception:
        raise HttpError(code=request.status, reason=CONN_ERROR, path=url)


def _find_notebook_path() -> Union[Tuple[dict, PurePath], Tuple[None, None]]:
    from traitlets.config import MultipleInstanceError

    try:
        kernel_id = _get_kernel_id()
    except (MultipleInstanceError, RuntimeError):
        return None, None  # Could not determine
    for server in _list_running_servers():
        try:
            sessions = _get_sessions(server)
            for sess in sessions:
                if sess["kernel"]["id"] == kernel_id:
                    return server, PurePath(sess["notebook"]["path"])  # nosec
        # There may be stale entries in the runtime directory
        except Exception:  # nosec
            pass  # nosec
    return None, None  # nosec


def notebook_name() -> str:
    """Returns the short name of the notebook w/o the .ipynb extension,
    or raises a FileNotFoundError exception if it cannot be determined.
    """
    _, path = _find_notebook_path()
    if path:
        return path.stem
    raise FileNotFoundError(FILE_ERROR.format("name"))


def notebook_path() -> Path:
    """Returns the absolute path of the notebook,
    or raises a FileNotFoundError exception if it cannot be determined.
    """
    srv, path = _find_notebook_path()
    if srv and path:
        root_dir = Path(srv.get("root_dir") or srv["notebook_dir"])
        return root_dir / path
    raise FileNotFoundError(FILE_ERROR.format("path"))


def auth_drive():
    """Authenticate Google Drive"""
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    from oauth2client.client import GoogleCredentials as GC
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.colab import auth

    SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    drive = None
    if os.getenv("GOOGLE_DRIVE_TOKEN"):
        creds = Credentials.from_authorized_user_file(os.getenv("GOOGLE_DRIVE_TOKEN"), SCOPES)
        drive = build("drive", "v3", credentials=creds, cache_discovery=False)
    elif os.getenv("GOOGLE_DRIVE_TOKEN") is None:
        auth.authenticate_user()
        gauth = GoogleAuth()
        gauth.credentials = GC.get_application_default()
        drive = GoogleDrive(gauth)
    return drive


def get_current_collab_notebook():
    """Get the filename, file_id of this notebook"""
    d = requests.get("http://172.28.0.2:9000/api/sessions").json()[0]
    filename = unquote(d["name"])
    file_id = d["path"].split("=")[1]
    return filename, file_id


def get_collab_path(file_id, drive=None):
    """
    Use file_id to get the file path in Google Drive

    NB needs to be mounted. User setup is conditional:

    from google.colab import drive
    drive.mount('/content/drive')
    """
    if drive is None:
        drive = auth_drive()
    f = drive.CreateFile({"id": file_id})
    name = f["title"]
    if f["parents"]:
        parent_id = f["parents"][0]["id"]
        return get_collab_path(parent_id, drive) / name
    else:
        return Path(name)


def _find_git_path(drive=None):
    """
    Find the git path relative to the google drive directory.
    """
    if drive is None:
        drive = auth_drive()
    file_list = drive.ListFile({"q": " title='.git' "}).GetList()
    return get_collab_path(file_list[0]["id"])


def get_absolute_path() -> str:
    """
    Get the path for the directory walk to check if there's a .git and initialize the Repo object.
    Relates to 'drive.mount('/content/drive')' as '/content/' is part of the path and 'drive/' is
    required or the path will not be found.
    """
    filename, file_id = get_current_collab_notebook()
    path = str(get_collab_path(file_id=file_id, drive=None))
    try:
        path_formatting = path.split("/")
        path_formatting.pop()
        completed_path = "/".join(path_formatting)
        return f"drive/{completed_path}/{filename}"
    except ValueError:
        return str(path)
