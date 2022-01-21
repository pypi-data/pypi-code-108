import pathlib
import re
import time
import traceback
from http.client import HTTPResponse, RemoteDisconnected
from socket import timeout
from typing import List
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import requests
from levo_commons.types import Headers
from requests.exceptions import InvalidHeader  # type: ignore
from requests.utils import check_header_validity  # type: ignore


def file_exists(path: str) -> bool:
    try:
        return pathlib.Path(path).is_file()
    except OSError:
        # For example, path could be too long
        return False


def fetch_schema_as_lines(schema_source: str) -> List[str]:
    """Fetch the schema file from the source (which can be a file or URL),
    delimited as lines.
    Note: need to add AuthN support later
    """
    schema_spec = []

    if file_exists(schema_source):
        try:
            with open(schema_source) as spec_file:
                schema_spec = spec_file.readlines()
                return schema_spec
        except:
            return schema_spec

    # If we get here, its likely a URL
    try:
        with requests.get(schema_source, stream=True) as spec_page:
            for line in spec_page.iter_lines(decode_unicode=True):
                if line:
                    schema_spec.append(line)
            return schema_spec
    except:
        return schema_spec


def format_exception(error: Exception, include_traceback: bool = False) -> str:
    """Format exception as text."""
    error_type = type(error)
    if include_traceback:
        lines = traceback.format_exception(error_type, error, error.__traceback__)
    else:
        lines = traceback.format_exception_only(error_type, error)
    return "".join(lines)


def is_latin_1_encodable(value: str) -> bool:
    """Header values are encoded to latin-1 before sending."""
    try:
        value.encode("latin-1")
        return True
    except UnicodeEncodeError:
        return False


# Adapted from http.client._is_illegal_header_value
INVALID_HEADER_RE = re.compile(r"\n(?![ \t])|\r(?![ \t\n])")  # pragma: no mutate


def has_invalid_characters(name: str, value: str) -> bool:
    try:
        check_header_validity((name, value))
        return bool(INVALID_HEADER_RE.search(value))
    except InvalidHeader:
        return True


def health_check_http_url(
    target_url: str,
    timeout_in_secs: int = 1,
    max_retry_count: int = 0,
    backoff_interval: int = 1,
) -> int:
    """
    Check the health of the specified HTTP/s URL.
    Retries the health check based on `max_retry_count`.
    Returns code `599` (Network Connect Timeout Error) on network errors.
    Returns the actual HTTP error code otherwise.
    """
    status_code = 599
    retry_count = 0
    while retry_count <= max_retry_count:
        try:
            status_code = urlopen(target_url, timeout=timeout_in_secs).status
        except (URLError, timeout, RemoteDisconnected) as e:
            if isinstance(e, HTTPError):
                status_code = e.code
            else:
                status_code = 599

            retry_count += 1
            if retry_count <= max_retry_count:
                sleep = backoff_interval * retry_count
                time.sleep(sleep)
        else:
            return status_code

    return status_code


SENSITIVE_HEADERS = ["Authorization", "authorization"]
SENSITIVE_HEADERS_MASK = {
    "Authorization": "AUTH_HEADER",
    "authorization": "AUTH_HEADER",
}


def mask_sensitive_headers(headers: Headers, sensitive_headers: List[str]) -> Headers:
    processed_headers: Headers = dict()
    for k, v in headers.items():
        if k not in sensitive_headers:
            processed_headers[k] = v
        else:
            processed_headers[k] = (
                SENSITIVE_HEADERS_MASK[k] if k in SENSITIVE_HEADERS_MASK else "***"
            )
    return processed_headers
