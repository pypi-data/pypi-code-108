"""This module contains various utility functions related to requests."""
import datetime
import logging

import pytz
from requests import Session
from six.moves import urllib

import myst_v1alpha1
from myst_v1alpha1.exceptions import MystAPIError
from myst_v1alpha1.utils.retry_utils import _DEFAULT_NUM_MAX_RETRIES
from myst_v1alpha1.utils.retry_utils import retry

_DEFAULT_RETRYABLE_HTTP_STATUSES = (
    429,  # Too Many Requests
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
)

logger = logging.getLogger(__name__)


@retry(num_max_retries=_DEFAULT_NUM_MAX_RETRIES)
def _make_request_check_status(request_url, method, session, auth, headers, data, retryable_status_codes):
    """Executes request to the specified url with the given method.

    Provides error handling for HTTP requests, including raising errors to be retried
    for certain retryable status codes.

    Args:
        request_url (str): the url used to fetch the JSON content
        method (str): HTTP request method (e.g. GET, POST, PUT, etc.)
        session (requests.Session): session to make request with
        auth (tuple, optional): auth tuple to enable Basic/Digest/Custom HTTP Auth
        headers (dict of str:str): HTTP header key:value pairs
        data (str): request body (for a POST request)
        retryable_status_codes (set): status codes to retry

    Returns:
        response (requests.Response): fetched HTTP response
    """
    # Use the session to make the request.
    # Note: Using the context manager ensures that the session closes any sockets after use.
    with session:
        response = session.request(method=method, url=request_url, headers=headers, data=data, auth=auth)

    if response.status_code in retryable_status_codes:
        response.raise_for_status()

    return response


def _make_request(
    request_url,
    method="GET",
    session=None,
    auth=None,
    headers=None,
    data=None,
    retryable_status_codes=_DEFAULT_RETRYABLE_HTTP_STATUSES,
):
    """Makes a request to the specified url with the given method.

    Handles retry-logic and error handling for HTTP requests.

    Args:
        request_url (str): the url used to fetch the JSON content
        method (str, optional): HTTP request method (e.g. GET, POST, PUT, etc.)
        session (requests.Session, optional): session to make request with
        auth (tuple, optional): auth tuple to enable Basic/Digest/Custom HTTP Auth
        headers (dict of str:str, optional): HTTP header key:value pairs
        data (str, optional): request body (for a POST request)
        retryable_status_codes (set, optional): status codes to retry; if not specified, a sensible default will be used

    Returns:
        response (requests.Response): fetched HTTP response
    """
    # If no session was given, construct a default session to use.
    if session is None:
        session = Session()

    logger.debug("Sending a {} request to {}.".format(method, request_url))

    response = _make_request_check_status(request_url, method, session, auth, headers, data, retryable_status_codes)
    response.raise_for_status()

    return response


def fetch_json_content(
    request_url,
    session=None,
    auth=None,
    headers=None,
    retryable_status_codes=_DEFAULT_RETRYABLE_HTTP_STATUSES,
):
    """Fetches JSON content using the passed request url.

    Args:
        request_url (str): the url used to fetch the JSON content
        session (requests.Session, optional): session to make request with
        auth (tuple, optional): auth tuple to enable Basic/Digest/Custom HTTP Auth
        headers (dict, optional): request headers to be passed
        retryable_status_codes (set, optional): status codes to retry; if not specified, a sensible default will be used

    Returns:
        json_content (dict): fetched JSON content
    """
    response = _make_request(
        request_url,
        session=session,
        auth=auth,
        headers=headers,
        retryable_status_codes=retryable_status_codes,
    )

    try:
        json_content = response.json()
    except ValueError as error:
        raise MystAPIError(
            http_status_code=response.status_code,
            code=response.status_code,
            message=str.format(
                "Failed to decode json response content. Error message: {error_message}. "
                "Response content: {response_content}.",
                error_message=str(error),
                response_content=response.content,
            ),
        )

    return json_content


def build_resource_url(resource_name, resource_uuid=None):
    """Builds the Myst API URL for a resource.

    Args:
        resource_name (str): resource name to build URL for
        resource_uuid (str, optional): resource instance uuid; if None, this function will just return the resource
            class url

    Returns:
        resource_url (str): resource url
    """
    api_base = urllib.parse.urljoin("{api_host}/".format(api_host=myst_v1alpha1.api_host), myst_v1alpha1.api_version)
    resource_url = urllib.parse.urljoin("{api_base}/".format(api_base=api_base), resource_name)
    if resource_uuid is not None:
        resource_url = urllib.parse.urljoin("{resource_url}/".format(resource_url=resource_url), resource_uuid)
    return resource_url


def encode_url(base_url, params):
    """Encodes the base url using the passed get parameters.

    Args:
        base_url (str): base url
        params (list of tuple): parameters to be used in the encoded url; note that even though `urllib.parse.urlencode`
            can take `params` in dictionary form, a list of tuple preserves order, whereas a dictionary does not

    Returns:
        encoded_url (str): encoded url
    """
    # Format any special parameter types that need to be formatted.
    formatted_params = []
    for param, value in params:
        if isinstance(value, datetime.datetime):
            value = format_timestamp(value)
        formatted_params.append((param, value))

    encoded_url = "{base_url}?{params}".format(base_url=base_url, params=urllib.parse.urlencode(formatted_params))
    return encoded_url


def format_timestamp(timestamp):
    """Formats the passed timestamp according to the RFC 3339 standard.

    Args:
        timestamp (datetime.datetime): timestamp to be formatted

    Returns:
        formatted_timestamp (str): formatted timestamp
    """
    if timestamp.tzinfo is None or timestamp.tzinfo is pytz.UTC:
        formatted_timestamp = "{}Z".format(timestamp.replace(tzinfo=None).isoformat())
    else:
        formatted_timestamp = timestamp.isoformat()
    return formatted_timestamp
