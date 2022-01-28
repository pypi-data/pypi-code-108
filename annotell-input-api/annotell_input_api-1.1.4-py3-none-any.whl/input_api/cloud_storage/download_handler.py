import json
import logging
from typing import Dict

import requests
import time

from requests.exceptions import HTTPError, ConnectionError
from requests.models import Response

from annotell.input_api.util import RETRYABLE_STATUS_CODES, get_wait_time

log = logging.getLogger(__name__)


class DownloadHandler:

    def __init__(self, max_retry_attempts: int = 23, max_retry_wait_time: int = 60, timeout: int = 60) -> None:
        """
        :param max_upload_retry_attempts: Max number of attempts to retry uploading a file to GCS.
        :param max_upload_retry_wait_time:  Max with time before retrying an upload to GCS.
        """
        self.max_num_retries = max_retry_attempts
        self.max_retry_wait_time = max_retry_wait_time  # seconds
        self.timeout = timeout  # seconds

    def get_json(self, url: str) -> Dict:
        return json.loads(self._download_file(url, self.max_num_retries))

    def _download_file(self, url: str, number_of_retries: int) -> bytes:
        """
        Download a json file from cloud storage

        :param url: URL of file to download
        :param number_of_retries: Number of download attempts before we stop trying to download
        :return: JSON deserialized to dictionary
        """
        resp = requests.get(url, timeout=self.timeout)
        try:
            resp.raise_for_status()
        except (HTTPError, ConnectionError) as e:
            http_condition = number_of_retries > 0 and resp.status_code in RETRYABLE_STATUS_CODES
            if http_condition or isinstance(e, ConnectionError):
                self._handle_download_error(resp, number_of_retries)
                self._download_file(url, number_of_retries - 1)
            else:
                raise e

        return resp.content

    def _handle_download_error(self, resp: Response, number_of_retries: int) -> None:
        download_attempt = self.max_num_retries - number_of_retries + 1
        wait_time = get_wait_time(download_attempt, self.max_retry_wait_time)
        log.error(
            f"Failed to download file. Got response: {resp.status_code}: {resp.content}"
            f"Attempt {download_attempt}/{self.max_num_retries}, retrying in {int(wait_time)} seconds."
        )
        time.sleep(wait_time)
