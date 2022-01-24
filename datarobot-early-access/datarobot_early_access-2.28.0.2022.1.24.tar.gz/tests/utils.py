#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import contextlib
import json
import re
import sys
import unittest
import warnings

import responses
from six.moves.urllib.parse import parse_qsl, unquote_plus, urlparse

from datarobot.client import set_client
from datarobot.rest import RESTClientObject


class SDKTestcase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        set_client(None)
        c = RESTClientObject(auth="t-token", endpoint="https://host_name.com")
        set_client(c)

    @classmethod
    def tearDownClass(cls):
        set_client(None)


@contextlib.contextmanager
def warns(*categories):
    """Assert warnings are raised in a block, analogous to pytest.raises."""
    with warnings.catch_warnings(record=True) as messages:
        yield messages
    assert tuple(message.category for message in messages) == categories


def assert_raised_regex(exc_info, regexp):
    """
    Until pytest 2.10 when this gets implemented as a method of exc_info,
    we will provide this assertion.

    This is the exact implementation that has already been merged to pytest

    Parameters
    ----------
    exc_info : pytest.ExceptionInfo
    regexp

    Returns
    -------

    """
    if not re.search(regexp, str(exc_info.value)):
        assert 0, "Pattern '{0!s}' not found in '{1!s}'".format(regexp, exc_info.value)
    return True


def assert_equal_py2(this, that):
    """Assert that arguments are equal on Python 2.

    This function does nothing on Python 3.
    """
    if sys.version_info < (3, 0):
        assert this == that


def assert_equal_py3(this, that, message=""):
    """Assert that arguments are equal on Python 3.

    This function does nothing on Python 2.
    """
    if sys.version_info >= (3, 0):
        assert this == that


def assert_urls_equal(url1, url2):
    """Assert that two URLs are equal taking into account quoting and order or parameters"""

    def get_parts(url):
        parts = urlparse(url)
        _query = frozenset(parse_qsl(parts.query))
        _path = unquote_plus(parts.path)
        parts = parts._replace(query=_query, path=_path)
        return parts

    assert get_parts(url1) == get_parts(url2), "{!r} != {!r}".format(url1, url2)


def request_body_to_json(request):
    """Extract json from body of prepared request from requests library.
    Request body is str in Python 2 and bytes in Python 3"""
    body = request.body
    if isinstance(body, bytes):
        return json.loads(body.decode())
    else:
        return json.loads(body)


def add_response(url, body, method=responses.GET, status=200, content_type="application/json"):
    if content_type == "application/json":
        body = json.dumps(body)
    responses.add(method, url, status=status, content_type=content_type, body=body)
