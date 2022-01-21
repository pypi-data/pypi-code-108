import abc
import logging

import time
from typing import Optional, Dict, Any

import requests

logger = logging.getLogger(__name__)


class ApiClientBase(abc.ABC):
    MAX_NUM_RETRIES_POLL = 10
    MAX_SLEEP_TIMEOUT = 32
    MAX_NUM_RETRIES_SUBMIT = 10

    def __init__(self, api_session: requests.Session, s3_session: requests.Session = requests.Session(),
                 max_sleep_timeout: int = MAX_SLEEP_TIMEOUT) -> None:
        self._api_session = api_session
        self._s3_session = s3_session
        self.max_sleep_timeout = max_sleep_timeout

    def _submit(self, url: str, data: bytes, query_id: str = "", pipeline_configuration: Optional[str] = None,
                max_num_retries: int = MAX_NUM_RETRIES_SUBMIT) -> str:
        additional_args = {}
        if pipeline_configuration:
            additional_args['pipeline_configuration'] = pipeline_configuration
        for i in range(max_num_retries):
            response = self._api_session.post(url, json={"query_id": query_id, **additional_args})
            if response.status_code == 200:
                response_data = response.json()
                response_put = self._s3_session.put(response_data["upload_url"], data=data, headers={'Content-Type': 'application/octet-stream'})
                response_put.raise_for_status()
                return response_data["submission_id"]
            if response.status_code == 500:  # we have experienced issues with this status code
                continue
            else:
                response.raise_for_status()
        raise RuntimeError("Submission unsuccessful, reached max number of retries.")

    def _poll(self, url: str, submission_id: str, max_num_retries: int = MAX_NUM_RETRIES_POLL, query_params: Optional[Dict[str, Any]] = None) -> dict:
        sleep_timeout = 1
        for i in range(max_num_retries):
            response = self._api_session.get(url.format(submission_id=submission_id), params=query_params)
            if response.status_code == 200:
                return response.json()
            if response.status_code == 404:
                logger.info("Submission not found. Waiting for retry...%d/%d", i, max_num_retries)
                time.sleep(min(sleep_timeout, self.max_sleep_timeout))
                sleep_timeout *= 2
            else:
                response.raise_for_status()
        raise RuntimeError("Submission not found, reached max number of retries.")
