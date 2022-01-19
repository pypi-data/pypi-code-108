import datetime
import json
import unittest

import mock
import pytz
from requests import HTTPError
from requests import Session
from six.moves import http_client
from tenacity import wait_none

from myst_v1alpha1.exceptions import MystAPIError
from myst_v1alpha1.utils.requests_utils import _make_request
from myst_v1alpha1.utils.requests_utils import build_resource_url
from myst_v1alpha1.utils.requests_utils import encode_url
from myst_v1alpha1.utils.requests_utils import fetch_json_content
from myst_v1alpha1.utils.requests_utils import format_timestamp


class MockResponse(object):
    """A mock response to use in tests."""

    def __init__(self, status_code, content=None, reason=None):
        super(MockResponse, self).__init__()
        self.status_code = status_code
        self.content = content
        self.reason = reason

    @property
    def ok(self):
        return self.status_code == http_client.OK

    def json(self):
        # As a temporary workaround to stay compatible with Python 2 and 3, fallback to passing a JSON string if in
        # Python 2.
        try:
            json_content = json.loads(self.content)
        except TypeError:
            json_content = json.loads(self.content.encode())

        return json_content

    def raise_for_status(self):
        if self.status_code == http_client.OK:
            return
        else:
            raise HTTPError


class RequestsUtilsTest(unittest.TestCase):
    @mock.patch("myst_v1alpha1.utils.retry_utils._retry_wait")
    def test_make_request_retry_logic_error_codes(self, _retry_wait_function_mock):
        """Raise error after four retries if status code is in the list of retryable exceptions."""
        # Mock tenacity's wait function so we don't actually sleep during tests.
        _retry_wait_function_mock.return_value = wait_none()

        # Create a session to test with.
        session = Session()

        with mock.patch.object(session, "request") as request_patch:
            # Test that by default we retry for 500, 502, 503, and 429 HTTP status codes.
            for status_code in [429, 500, 502, 503, 504]:
                request_patch.return_value = MockResponse(status_code=status_code, content="", reason="Retry later.")
                self.assertRaises(
                    HTTPError,
                    _make_request,
                    session=session,
                    request_url="https://www.domain.com?param=value",
                    headers={"key": "value"},
                    data="example_data",
                )
                self.assertEqual(4, request_patch.call_count)

                # Reset mocks for next status code.
                request_patch.reset_mock()

    @mock.patch("myst_v1alpha1.utils.retry_utils._retry_wait")
    def test_make_request_no_retry_logic_error_codes(self, _retry_wait_function_mock):
        """Raise error immediately if status code is not in the list of retryable exceptions."""
        # Mock tenacity's wait function so we don't actually sleep during tests.
        _retry_wait_function_mock.return_value = wait_none()

        # Create a session to test with.
        session = Session()

        with mock.patch.object(session, "request") as request_patch:
            # Test that IO error is raised immediately for a status code not in the retry list.
            for status_code in [400]:
                request_patch.return_value = MockResponse(status_code=status_code, content="", reason="Retry later.")
                self.assertRaises(
                    HTTPError,
                    _make_request,
                    session=session,
                    request_url="https://www.domain.com?param=value",
                    headers={"key": "value"},
                    data="example_data",
                )
                self.assertEqual(1, request_patch.call_count)

                # Reset mocks for next status code.
                request_patch.reset_mock()

    @mock.patch("myst_v1alpha1.utils.retry_utils._retry_wait")
    def test_make_request_retry_logic_exceptions(self, _retry_wait_function_mock):
        # Mock tenacity's wait function so we don't actually sleep during tests.
        _retry_wait_function_mock.return_value = wait_none()

        # Create a session to test with.
        session = Session()

        with mock.patch.object(session, "request") as request_patch:
            # Test that we retry various python errors.
            for exception_cls in [IOError, OSError, ValueError]:
                request_patch.side_effect = exception_cls("An exception occurred.")

                self.assertRaises(
                    exception_cls,
                    _make_request,
                    session=session,
                    request_url="https://www.domain.com?param=value",
                    headers={"key": "value"},
                    data="example_data",
                )
                self.assertEqual(4, request_patch.call_count)

                # Reset mocks for next status code.
                request_patch.reset_mock()

    def test_fetch_json_content(self):
        # Create a session to test with.
        session = Session()

        with mock.patch.object(session, "request") as request_patch:
            request_patch.return_value = MockResponse(status_code=http_client.OK, content=json.dumps({"key": "value"}))
            self.assertEqual(
                fetch_json_content(request_url="https://www.domain.com", session=session), {"key": "value"}
            )

            # Test that an error is raised if the json is malformed.
            request_patch.return_value = MockResponse(
                status_code=http_client.OK,
                content=json.dumps({"key": "value"}) + json.dumps({"key": "value"}),  # Invalid duplicate json objects
            )
            self.assertRaises(MystAPIError, fetch_json_content, request_url="https://www.domain.com", session=session)

    def test_build_resource_url(self):
        self.assertEqual(build_resource_url(resource_name="resource"), "https://api.myst.ai/v1alpha1/resource")
        self.assertEqual(
            build_resource_url(resource_name="resource", resource_uuid="4b84d6c0-b7c0-450c-b836-9f0402ad681c"),
            "https://api.myst.ai/v1alpha1/resource/4b84d6c0-b7c0-450c-b836-9f0402ad681c",
        )

    def test_encode_url(self):
        self.assertEqual(
            encode_url(base_url="myst.ai", params=[("key_1", "value_1"), ("key_2", "value_2")]),
            "myst.ai?key_1=value_1&key_2=value_2",
        )

    def test_format_timestamp(self):
        utc_timezone = pytz.timezone("UTC")
        denver_timezone = pytz.timezone("America/Denver")

        # Test that by default, we assume timezone-naive timestamps are in UTC.
        self.assertEqual(format_timestamp(timestamp=datetime.datetime(2018, 1, 1, 12, 42, 12)), "2018-01-01T12:42:12Z")

        # Test that we format timezone-aware timestamps according to their timezones.
        self.assertEqual(
            format_timestamp(timestamp=utc_timezone.localize(datetime.datetime(2018, 1, 1, 12, 42, 12))),
            "2018-01-01T12:42:12Z",
        )
        self.assertEqual(
            format_timestamp(timestamp=denver_timezone.localize(datetime.datetime(2018, 1, 1, 12, 42, 12))),
            "2018-01-01T12:42:12-07:00",
        )
