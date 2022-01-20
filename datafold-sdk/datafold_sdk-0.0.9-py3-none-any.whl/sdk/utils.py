from typing import Sequence
import logging
import subprocess
import os

from urllib.parse import urlparse
import requests


logger = logging.getLogger(__file__)


def prepare_api_url(host: str, api_segment: str):
    return os.path.join(host, api_segment)


def prepare_headers(api_key: str):
    headers = {
        "Authorization": "Key " + api_key,
    }
    return headers


def run_command(cmd_list, capture=True, cwd="."):
    try:
        process = subprocess.run(cmd_list, check=True, capture_output=capture, cwd=cwd)
        return process.stdout.decode('UTF-8').strip()
    except subprocess.CalledProcessError as exception:
        logger.error("The process failed")
        logger.error(exception.stderr)
        logger.error(exception.stdout)
        raise exception


def post_data(url, data=None, json=None, headers=None, files=None):
    try:
        res = requests.post(url, files=files, data=data, json=json, headers=headers)
        check_requests_result(res)
        return res
    except requests.exceptions.ConnectionError as exception:
        parsed_uri = urlparse(url)
        logger.error(f"The host {parsed_uri.netloc} could not be reached")
        raise exception


def get_data(url, headers, params=None):
    try:
        res = requests.get(url, headers=headers, params=params or {})
        check_requests_result(res)
        return res
    except requests.exceptions.ConnectionError as exception:
        parsed_uri = urlparse(url)
        logger.error(f"The host {parsed_uri.netloc} could not be reached")
        raise exception


def check_requests_result(res):
    res.raise_for_status()


def print_table(rows: Sequence[Sequence[str]]):
    lengths = [max(len(v) for v in column) for column in zip(*rows)]
    fmt = ' '.join(f'%-{x + 1}s' for x in lengths)
    for row in rows:
        print(fmt % row)
