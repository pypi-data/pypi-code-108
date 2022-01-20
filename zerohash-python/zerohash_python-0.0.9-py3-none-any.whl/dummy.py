# REFERENCE CODE FROM THE API DOCS
import hashlib
import hmac
import json
from base64 import b64decode, b64encode
from datetime import datetime
from logging import getLogger
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from dotenv import find_dotenv, load_dotenv

logger = getLogger(__name__)
import os

# NB: THESE CREDENTIALS SHOULD NOT BE STORED IN PLAINTEXT
# Keys here are kept in plaintext for the purposes of demonstration
# We encourage you to encrypt your keys and decrypt them only when being used
load_dotenv(find_dotenv())
URL_BASE = "api.cert.zerohash.com"
HTTP_BASE = "https://" + URL_BASE
API_PUBLIC_KEY = os.environ["PUBLIC_KEY"]  # "usjHuLksaeBXWSsa8uU7ES"
API_PRIVATE_KEY = os.environ[
    "PRIVATE_KEY"
]  # 2mC4ZvVd4goRkuJm+rjr9byUiaUW1b6tVN4xy9QXNSE=
PASSPHRASE = os.environ["PASSPHRASE"]  # testingisgreat


def sign(
    api_key: str, method: str, route: str, json_body: str, timestamp: str
) -> bytes:
    """Given a key and data, create and sign a payload.

    :param api_key: Key to sign the message with
    :param method: HTTP method
    :param route: Relative route. EX. /fills
    :param json_body: JSON as a string. Usually created via json.dumps(dict)
    :param timestamp: Unix Epoch time as a string
    :return: Base64 encoded digest
    """
    msg = bytes(timestamp + method + route + json_body, encoding="utf-8")
    hm = hmac.new(key=b64decode(api_key), msg=msg, digestmod=hashlib.sha256)
    return b64encode(hm.digest())


def headers() -> Dict[str, Any]:
    """Create a header template for use in HTTP requests."""
    return {
        "X-SCX-API-KEY": API_PUBLIC_KEY,
        "X-SCX-SIGNED": "",  # Put here to make sure we alway send something
        # The datetime.timestamp function is available only in Python 3.3+
        "X-SCX-TIMESTAMP": str(int(datetime.now().timestamp())),  # Unix Epoch
        "X-SCX-PASSPHRASE": PASSPHRASE,
    }


def make_seed_request(
    method: str, url: str, body: Optional[Dict[str, str]] = None
) -> requests.Response:
    """Create and send an HTTP request with a signature to the Zero Hash API.

    :param method: HTTP method
    :param url: Relative route. EX. /fills
    :param body: Dictionary for serializing into the JSON body of the request. For GET requests,
                 this can be omitted or set to an empty dict. Nothing will be sent, but it is
                 required for the signature.
    :return: requests.Response object
    """
    if body is None:
        body = {}
    h = headers()
    json_body = json.dumps(body, separators=(",", ":"))
    h["X-SCX-SIGNED"] = sign(
        API_PRIVATE_KEY, method, url, json_body, h["X-SCX-TIMESTAMP"]
    )
    args = {"method": method, "url": urljoin(HTTP_BASE, url)}
    logger.info("Making {} request to {}".format(method, urljoin(URL_BASE, url)))
    if body:
        args["data"] = json_body
        h["Content-Type"] = "application/json"
        logger.debug(json_body)
    args["headers"] = h
    print(args)
    # Since we don't know if it's a GET or POST, use the generic request function and create an
    # args dict so that we can conditionally pass data/JSON
    return requests.request(**args)


def make_seed_reqauest_hardcoded():
    body = {}
    h = {
        "X-SCX-API-KEY": "dhMsj1QcGP3TsepKPRBRcW",
        "X-SCX-SIGNED": "",  # Put here to make sure we alway send something
        # The datetime.timestamp function is available only in Python 3.3+
        "X-SCX-TIMESTAMP": "1633116917",
        "X-SCX-PASSPHRASE": "thisiscool",
    }
