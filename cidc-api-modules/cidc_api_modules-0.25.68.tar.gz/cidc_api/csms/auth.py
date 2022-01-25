__all__ = ["get_token", "get_with_authorization", "get_with_paging"]
import os

os.environ["TZ"] = "UTC"
from datetime import datetime, timedelta
from typing import Any, Dict, Iterator
import requests

from ..config.settings import (
    CSMS_BASE_URL,
    CSMS_CLIENT_ID,
    CSMS_CLIENT_SECRET,
    CSMS_TOKEN_URL,
)


_TOKEN, _TOKEN_EXPIRY = None, datetime.now()


def get_token():
    global _TOKEN, _TOKEN_EXPIRY
    if not _TOKEN or datetime.now() >= _TOKEN_EXPIRY:
        res, time = (
            requests.post(
                CSMS_TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "client_credentials",
                    "client_id": CSMS_CLIENT_ID,
                    "client_secret": CSMS_CLIENT_SECRET,
                },
            ).json(),
            datetime.now(),
        )

        # res definition from https://developer.okta.com/docs/reference/api/oidc/#response-example-error-7
        if "errorCode" in res:
            raise Exception(res["errorCode"] + ": " + res.get("errorSummary"))

        _TOKEN = res["access_token"]
        _TOKEN_EXPIRY = time + timedelta(seconds=res["expires_in"])

    return _TOKEN


def get_with_authorization(url: str, **kwargs) -> requests.Response:
    """url should be fully valid or begin with `/` to be prefixed with CSMS_BASE_URL"""
    token = get_token()
    headers = {
        **kwargs.get("headers", {}),
        "Authorization": f"Bearer {token}",
        "accept": "*/*",
    }
    kwargs["headers"] = headers
    if not url.startswith(CSMS_BASE_URL):
        url = CSMS_BASE_URL + url
    return requests.get(url, **kwargs)


def get_with_paging(
    url: str, limit: int = None, offset: int = 0, **kwargs
) -> Iterator[Dict[str, Any]]:
    """
    Return an iterator of entries via get_with_authorization with handling for CSMS paging
    
    Parameters
    ----------
    url: str
        url should be fully valid or begin with `/` to be prefixed with CSMS_BASE_URL
    limit: int = None
        the number of records to return on each page
        default: 5000 for samples, 50 for manifests, 1 otherwise
    offset: int = 0
        which page to return, 0-indexed
        increments as needed to continue returning

    Raises
    ------
    requests.exceptions.HTTPError
        via res.raise_for_status()
        https://docs.python-requests.org/en/master/user/quickstart/#response-status-codes
    """
    if not limit:
        if "samples" in url:
            limit = 5000
        elif "manifests" in url:
            limit = 50
        else:
            limit = 1

    kwargs.update(dict(limit=limit, offset=offset))

    res = get_with_authorization(url, params=kwargs)
    while res.status_code < 300 and len(res.json().get("data", [])) > 0:
        # if there's not an error and we're still returning
        yield from res.json()["data"]
        kwargs["offset"] += 1  # get the next page
        res = get_with_authorization(url, params=kwargs)
    else:
        res.raise_for_status()
