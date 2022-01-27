""" test data

   isort:skip_file
"""

import unittest
import os
import sys

try:
    from unittest import mock
except ImportError:
    import mock

from mock import MagicMock

from ciocore import api_client


class ApiClientTest(unittest.TestCase):
    @staticmethod
    def path_exists_side_effect(arg):
        if "missing" in arg:
            return False
        else:
            return True

    def setUp(self):
        self.env = {"HOME": "/users/joebloggs"}

        self.api_key_dict = {"api_key": {"client_id": "123", "private_key": "secret123"}}

        patcher = mock.patch("os.path.exists")
        self.mock_exists = patcher.start()
        self.mock_exists.side_effect = ApiClientTest.path_exists_side_effect
        self.addCleanup(patcher.stop)

    def test_create(self):
        ac = api_client.ApiClient()
        self.assertEqual(ac.__class__.__name__, "ApiClient")

    def test_get_standard_creds_path(self):
        with mock.patch.dict("os.environ", self.env):
            fn = api_client.get_creds_path(api_key=False)
            self.assertEqual(fn, "/users/joebloggs/.config/conductor/credentials")

    def test_get_api_key_creds_path(self):
        with mock.patch.dict("os.environ", self.env):
            fn = api_client.get_creds_path(api_key=True)
            self.assertEqual(fn, "/users/joebloggs/.config/conductor/api_key_credentials")

