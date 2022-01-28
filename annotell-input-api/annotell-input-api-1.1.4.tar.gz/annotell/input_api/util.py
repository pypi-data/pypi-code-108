"""Utility functions for Input API """

import mimetypes
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
import random
from PIL import Image as PILImage
from typing import List, Dict

import dateutil.parser
from urllib3.util import Url, parse_url

GCS_SCHEME = "gs"

RETRYABLE_STATUS_CODES = [408, 429, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 598, 599]


def ts_to_dt(date_string: str) -> datetime:
    """
    Parse string datetime into datetime
    """
    return dateutil.parser.parse(date_string)


def filter_none(js: dict) -> dict:
    if isinstance(js, Mapping):
        return {k: filter_none(v) for k, v in js.items() if v is not None}
    else:
        return js


def get_content_type(filename: str) -> str:
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
    if filename.split(".")[-1] == "csv":
        content_type = "text/csv"
    else:
        content_type = mimetypes.guess_type(filename)[0]
        content_type = content_type if content_type is not None else 'application/octet-stream'

    return content_type


def get_resource_id(signed_url: str) -> str:
    url = parse_url(signed_url)
    resource_id = Url(scheme=GCS_SCHEME, path=url.path)
    return str(resource_id).replace("///", "//")


def get_image_dimensions(image_path: str) -> dict:
    fi = Path(image_path).expanduser()
    with PILImage.open(fi) as im:
        width, height = im.size
        return {"width": width, "height": height}


def get_view_links(input_uuids: List[str]) -> Dict[str, str]:
    """
        For each given input uuid returns an URL where the input can be viewed in the web app.

        :param input_uuids: List with input uuids
        :return Dict: Dictionary mapping each uuid with an URL to view the input.
        """
    view_dict = dict()
    for input_uuid in input_uuids:
        view_dict[input_uuid] = f"https://app.annotell.com/input-view/{input_uuid}"

    return view_dict


# https://cloud.google.com/iot/docs/how-tos/exponential-backoff
def get_wait_time(upload_attempt: int, max_retry_wait_time: int) -> float:
    """
    Calculates the wait time before attempting another file upload or download

    :param upload_attempt: How many attempts to upload that have been made
    :return: int: The time to wait before retrying upload
    """
    initial_wait_time_seconds: int = pow(2, upload_attempt - 1)
    wait_time_seconds: float = initial_wait_time_seconds + random.random()
    wait_time_seconds: float = wait_time_seconds if wait_time_seconds < max_retry_wait_time else max_retry_wait_time
    return wait_time_seconds
