"""Handler for file upload/download."""
import os
from typing import List, Optional, Tuple
import requests

import tenacity

from redbrick_slicer.common.constants import MAX_RETRY_ATTEMPTS


def uniquify_path(path: str) -> str:
    """Provide unique path with number index."""
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path


def download_files(files: List[Tuple[str, str]]) -> List[Optional[str]]:
    """Download files from url to local path."""

    @tenacity.retry(
        reraise=True,
        stop=tenacity.stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=tenacity.wait_exponential(multiplier=1, min=1, max=10),
        retry=tenacity.retry_if_not_exception_type(
            (KeyboardInterrupt, PermissionError, ValueError)
        ),
    )
    def _download_file(url: str, path: str) -> Optional[str]:
        if not url or not path:
            return None
        response = requests.get(url)
        if response.status_code == 200:
            path = uniquify_path(path)
            with open(path, "wb") as file_:
                file_.write(response.content)
            return path
        return None

    paths = []
    for url, path in files:
        paths.append(_download_file(url, path))

    return paths
