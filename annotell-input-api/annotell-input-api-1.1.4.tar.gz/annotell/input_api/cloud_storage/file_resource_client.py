"""Client for communicating with the Annotell platform."""
import logging
from pathlib import Path
from typing import Dict, Mapping, Optional, BinaryIO

from annotell.input_api.cloud_storage.download_handler import DownloadHandler
from annotell.input_api.cloud_storage.upload_handler import UploadHandler

log = logging.getLogger(__name__)


class FileResourceClient:

    def __init__(self, max_retry_attempts: int = 23, max_retry_wait_time: int = 60, timeout: int = 60):
        """
        :param max_upload_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_upload_retry_wait_time:  Max with time before retrying an upload to GCS.
        """
        self._upload_handler = UploadHandler(max_retry_attempts, max_retry_wait_time, timeout)
        self._download_handler = DownloadHandler(max_retry_attempts, max_retry_wait_time, timeout)

    def upload_files(self, url_map: Mapping[str, str], folder: Optional[Path] = None) -> None:
        """
        Upload all files to cloud storage

        :param url_map: map between filename and GCS signed URL
        :param folder: Optional base path, will join folder and each filename in map if provided
        """
        self._upload_handler.upload_files(url_map=url_map, folder=folder)

    def upload_json(self, file: BinaryIO, url: str) -> None:
        """
        Upload a single file to storage, using the specified url
        :param file: A binary representation of the file
        :param url: The url ot upload to file to
        """

        self._upload_handler.upload_file(file, url)

    def get_json(self, url: str) -> Dict:
        """
        Downloads a json from cloud storage

        :param url: Signed URL to GCS resource to download
        """
        return self._download_handler.get_json(url)
