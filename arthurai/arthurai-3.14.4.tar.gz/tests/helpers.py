import json
from datetime import datetime
from http import HTTPStatus
from typing import Dict, Any, Union, List, Tuple
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytz
import responses

from arthurai import ArthurAttribute
from tests.fixtures.mocks import BASE_URL

from unittest import TestCase

CONTENT_TYPE_JSON = 'application/json'
OK_DEFAULT_STATUS = HTTPStatus.OK


def mock_response(request_type: str, append_url: str, response_body: Union[Dict, List, str, bytes],
                  status=OK_DEFAULT_STATUS, headers: Dict[str, str] = None):
    """
    Adds a mock response

    :param request_type: the type of HTTP request expected (e.g. GET)
    :param append_url: the url to the base url
    :param response_body: the response to return from the mock API request
    :param status: status code of the response
    :param headers: content type header of the returned response

    :return: None
    """
    if headers is None:
        headers = {}
    # responses likes the content type header to be specified as a param
    content_type = headers.pop('Content-Type', CONTENT_TYPE_JSON)

    parsed_body: Union[str, bytes] = ""
    if isinstance(response_body, list) or isinstance(response_body, dict):
        parsed_body = json.dumps(response_body)
    else:
        parsed_body = response_body

    responses.add(request_type, BASE_URL + append_url, parsed_body, status=status, headers=headers,
                  content_type=content_type)


def mock_post(append_url: str, response_body: Union[Dict, List, str, bytes], status=OK_DEFAULT_STATUS,
              headers: Dict[str, str] = None):
    """
    Adds a mock 200 response to a POST request

    :param append_url: the url to the base url
    :param response_body: the response to return from the mock API request
    :param status: status code of the response
    :param headers: content type header of the returned response

    :return: None
    """
    mock_response(responses.POST, append_url, response_body, status=status, headers=headers)


def mock_patch(append_url: str, response_body: Union[Dict, List, str, bytes], status=OK_DEFAULT_STATUS,
               headers: Dict[str, str] = None):
    """
    Adds a mock 200 response to a PATCH request

    :param append_url: the url to the base url
    :param response_body: the response to return from the mock API request
    :param status: status code of the response
    :param headers: content type header of the returned response

    :return: None
    """
    mock_response(responses.PATCH, append_url, response_body, status=status, headers=headers)


def mock_get(append_url: str, response_body: Union[Dict, List, str, bytes], status=200, headers: Dict[str, str] = None):
    """
    Adds a mock 200 response

    :param append_url: the url to the base url
    :param response_body: the response to return from the mock API request
    :param status: status code of the response
    :param headers: headers of the returned response

    :return: None
    """
    mock_response(responses.GET, append_url, response_body, status=status, headers=headers)


class MockShortUUID:
    def __init__(self, ids=None):
        if ids is None:
            self.ids = []
        else:
            self.ids = ids
        self.next_idx = 0

    def call_count(self):
        return self.next_idx

    def next(self):
        value = self.ids[self.next_idx]
        self.next_idx += 1
        return value


class MockDatetime:
    def __init__(self, return_vals=None, return_raw_strings=False):
        if return_vals is None or len(return_vals) == 0:
            self.timestamps = []
        else:
            if isinstance(return_vals[0], datetime):
                self.timestamps = return_vals
            elif isinstance(return_vals[0], str):
                mocks = []
                for ts in return_vals:
                    if return_raw_strings:
                        mocks.append(ts)
                    else:
                        dt = MagicMock(datetime)
                        dt.isoformat.return_value = ts
                        mocks.append(dt)
                self.timestamps = mocks
        self.next_idx = 0

    def call_count(self):
        return self.next_idx

    def next(self, tz):
        if tz != pytz.utc:
            raise ValueError("unexpected timezone")
        value = self.timestamps[self.next_idx]
        self.next_idx += 1
        return value


def assert_kwargs_equal(actual: Dict[str, Any], expected: Dict[str, Any]):
    assert actual.keys() == expected.keys()
    for key in expected.keys():
        if isinstance(actual[key], (pd.Series, pd.DataFrame)):
            assert actual[key].equals(expected[key])
        elif isinstance(actual[key], np.ndarray):
            assert np.equal(actual[key], expected[key]).all()
        else:
            assert actual[key] == expected[key]


def assert_attributes_equal(expected: List[ArthurAttribute], actual: List[ArthurAttribute]):
    # create a map from attribute name to the index in the list
    expected_name_to_index = {attr.name: i for i, attr in enumerate(expected)}
    actual_name_to_index = {attr.name: i for i, attr in enumerate(actual)}
    if len(expected_name_to_index) != len(expected) or len(actual_name_to_index) != len(actual):
        raise ValueError("attributes in lists have duplicate names")

    # create pairs of the matching attributes to compare to each other
    expected_actual_pairs: List[Tuple[ArthurAttribute, ArthurAttribute]] = []
    missing_attrs = []
    for expected_attr in expected:
        if expected_attr.name not in actual_name_to_index.keys():
            missing_attrs.append(expected_attr.name)
        else:
            expected_actual_pairs.append((expected_attr, actual[actual_name_to_index[expected_attr.name]]))

    extra_attrs = []
    for actual_attr in actual:
        if actual_attr.name not in expected_name_to_index.keys():
            extra_attrs.append(actual_attr.name)
    assert len(missing_attrs) == 0, f"actual attributes list is missing: {', '.join(missing_attrs)}"

    # iterate through pairs, comparing their values
    failures = []
    for expected_attr, actual_attr in expected_actual_pairs:
        # assert each field is the same, but categories field can have different order
        try:
            assert expected_attr.name == actual_attr.name
            assert expected_attr.stage == actual_attr.stage
            assert expected_attr.id == actual_attr.id
            assert expected_attr.position == actual_attr.position
            assert expected_attr.categorical == actual_attr.categorical
            assert expected_attr.min_range == actual_attr.min_range
            assert expected_attr.monitor_for_bias == actual_attr.monitor_for_bias
            if expected_attr.categories is None:
                assert actual_attr.categories is None
            else:
                TestCase().assertCountEqual(expected_attr.categories, actual_attr.categories)
            assert expected_attr.bins == actual_attr.bins
            assert expected_attr.is_unique == actual_attr.is_unique
            assert expected_attr.attribute_link == actual_attr.attribute_link
        except AssertionError as e:
            failures.append(f"Attribute {expected_attr.name} does not match expected value.\nActual:   {actual_attr}\n"
                            f"Expected: {expected_attr}\nError: {e}")
    assert len(failures) == 0, "\n".join(failures)
