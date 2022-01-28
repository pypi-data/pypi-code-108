import logging
import time
from pathlib import Path
from typing import BinaryIO, Dict, Mapping, Optional

import requests
from requests.exceptions import HTTPError, ConnectionError
from requests.models import Response

from annotell.input_api.util import RETRYABLE_STATUS_CODES, get_content_type, get_wait_time

log = logging.getLogger(__name__)


class UploadHandler:

    def __init__(self, max_retry_attempts: int = 23, max_retry_wait_time: int = 60, timeout: int = 60) -> None:
        """
        :param max_upload_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_upload_retry_wait_time:  Max with time before retrying an upload to GCS.
        """
        self.max_num_retries = max_retry_attempts
        self.max_retry_wait_time = max_retry_wait_time  # seconds
        self.timeout = timeout  # seconds

    #  Using similar retry strategy as gsutil
    #  https://cloud.google.com/storage/docs/gsutil/addlhelp/RetryHandlingStrategy
    def _upload_file(self, upload_url: str, file: BinaryIO, headers: Dict[str, str], number_of_retries: int) -> None:
        """
        Upload the file to GCS, retries if the upload fails with some specific status codes.
        """
        if hasattr(file, "name"):
            log.info(f"Uploading file={file.name}")
        else:
            log.info(f"Uploading in memory data")
        resp = requests.put(upload_url, data=file, headers=headers, timeout=self.timeout)
        try:
            resp.raise_for_status()
        except (HTTPError, ConnectionError) as e:
            http_condition = number_of_retries > 0 and resp.status_code in RETRYABLE_STATUS_CODES
            if http_condition or isinstance(e, ConnectionError):
                self._handle_upload_error(resp, number_of_retries)
                self._upload_file(upload_url, file, headers, number_of_retries - 1)
            else:
                raise e

    def _handle_upload_error(self, resp: Response, number_of_retries: int):
        upload_attempt = self.max_num_retries - number_of_retries + 1
        wait_time = get_wait_time(upload_attempt, self.max_retry_wait_time)
        log.error(
            f"Failed to upload file. Got response: {resp.status_code}: {resp.content}"
            f"Attempt {upload_attempt}/{self.max_num_retries}, retrying in {int(wait_time)} seconds."
        )
        time.sleep(wait_time)

    def upload_files(self, url_map: Mapping[str, str], folder: Optional[Path] = None) -> None:
        """
        Upload all files to cloud storage

        :param url_map: map between filename and GCS signed URL
        :param folder: Optional base path, will join folder and each filename in map if provided
        """
        for (filename, upload_url) in url_map.items():
            file_path = folder.joinpath(filename).expanduser() if folder else Path(filename).expanduser()
            with file_path.open('rb') as file:
                content_type = get_content_type(filename)
                headers = {"Content-Type": content_type}
                self._upload_file(upload_url, file, headers, self.max_num_retries)

    def upload_file(self, file: BinaryIO, url: str) -> None:
        """

        :param file:
        :param url:
        """
        headers = {"Content-Type": "application/json"}
        self._upload_file(url, file, headers, self.max_num_retries)
