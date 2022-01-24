import json
import logging
import os
import types
import urllib.parse
from pathlib import Path
from typing import Text, Optional, Any, Dict, List, Tuple

import requests
from notebook.utils import url_path_join
from pkg_resources._vendor.packaging.version import Version

from jupyter_cogram import __version__

logger: logging.Logger = logging.getLogger(__name__)

timeout_in_seconds = 5

config_location = Path().home() / ".ipython/nbextensions/jupyter-cogram"
cached_file = "cogram_server.json"

debug_mode = os.getenv("DEBUG_MODE", "false") == "true"

backend_url = os.getenv("BACKEND_URL", "https://api.cogram.com")

DEFAULT_CDN_PATHS = [
    {
        "metadata_url": f"https://storage.googleapis.com/storage/v1/b/cogram-public/o/{urllib.parse.quote_plus('jupyter-cogram/latest/server.min.py')}",
        "source_url": "https://storage.googleapis.com/cogram-public/jupyter-cogram/latest/server.min.py",
    }
]


def import_from_bytes(
    byte_io: bytes, file_name: Text, module_name: Optional[Text] = None
) -> types.ModuleType:
    value = compile(byte_io, file_name, "exec")
    module = types.ModuleType(module_name)
    exec(value, module.__dict__)

    return module


def import_from_url(
    url: Text, module_name: Optional[Text] = None, version: Optional[Text] = None
) -> types.ModuleType:
    file_name = os.path.basename(url).lower()
    if not module_name:
        module_name = os.path.splitext(file_name)[0]

    logger.debug(f"Importing module '{module_name}' from url '{url}'")
    r = requests.get(url, timeout=timeout_in_seconds)
    r.raise_for_status()

    content: bytes = r.content

    obj_to_dump = {"version": version, "content": content.decode("utf-8")}

    with (config_location / cached_file).open("w") as f:
        json.dump(obj_to_dump, f)

    return import_from_bytes(content, file_name, module_name)


def get_latest_version(metadata_url: Text) -> Version:
    r = requests.get(metadata_url, timeout=timeout_in_seconds)
    r.raise_for_status()
    rjs = r.json()
    return Version(rjs.get("metadata", {}).get("version", "0.0.0"))


def read_cached_file() -> Dict[Text, Any]:
    local_path = config_location / cached_file
    if not local_path.exists():
        logger.debug("Local cached file not found.")
        return {}

    with local_path.open() as f:
        logger.debug("Found local cached file.")
        return json.load(f)


def get_cdn_urls() -> Tuple[bool, List[Dict]]:
    url = urllib.parse.urljoin(backend_url, "info")
    logger.debug(f"Checking CDN files from {url}")
    # noinspection PyBroadException
    try:
        r = requests.get(
            url,
            params={"installed_version": __version__},
            timeout=timeout_in_seconds,
        )
        r.raise_for_status()
        rjs = r.json()
        return (
            rjs["is_development_deployment"],
            rjs["jupyter_cogram"]["python_sources"],
        )
    except:
        return False, DEFAULT_CDN_PATHS


def import_cogram_server() -> Any:
    is_dev_deployment, cdn_urls = get_cdn_urls()

    if is_dev_deployment:
        logger.debug("Have development deployment.")
        return import_from_url(
            cdn_urls[0]["source_url"],
            "jupyter_cogram_serverextension",
            version="0.11.23",
        )

    latest_version = get_latest_version(cdn_urls[0]["metadata_url"])
    cached = read_cached_file()

    logger.debug(f"Have latest version from CDN {latest_version}")

    cached_version = Version(cached.get("version", "0.0.0"))
    logger.debug(f"Have cached version {cached_version}")

    def load_from_cdn():
        return import_from_url(
            cdn_urls[0]["source_url"],
            "jupyter_cogram_serverextension",
            version=str(latest_version),
        )

    if latest_version > cached_version:
        logger.debug("Fetching new version from CDN")
        return load_from_cdn()

    # noinspection PyBroadException
    try:
        logger.debug("Will load locally cached version.")
        return import_from_bytes(
            cached.get("content", "").encode("utf-8"),
            "server.py",
            "jupyter_cogram_serverextension",
        )
    except Exception:
        logger.error("Failed to load cached version. Will load from CDN.")
        return load_from_cdn()


def load_jupyter_server_extension(nb_server_app) -> None:
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication):
        handle to the Notebook webserver instance.
    """
    if debug_mode:
        logging.basicConfig(level=logging.DEBUG)

    cogram_server = import_cogram_server()

    web_app = nb_server_app.web_app
    host_pattern = ".*$"
    web_app.add_handlers(
        host_pattern,
        [
            (url_path_join(web_app.settings["base_url"], uri), handler)
            for uri, handler in cogram_server.HANDLERS
        ],
    )
    logger.debug("loaded_jupyter_server_extension: jupyter-cogram")
