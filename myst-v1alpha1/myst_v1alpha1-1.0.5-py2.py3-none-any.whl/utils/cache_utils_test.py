import json
import os
import tempfile
import unittest

import google.oauth2.credentials
import mock

from myst_v1alpha1.utils.cache_utils import get_local_app_config_path
from myst_v1alpha1.utils.cache_utils import load_user_credentials
from myst_v1alpha1.utils.cache_utils import save_user_credentials


class CacheUtilsTest(unittest.TestCase):
    def test_get_user_credentials_cache_path(self):
        # Patch os.name (platform name) and `APPDATA` so make it seem like we're on a Windows system.
        with mock.patch("myst_v1alpha1.utils.auth_utils.os.name", "nt"):
            with mock.patch.dict(os.environ, dict(APPDATA="/path/to/app/data")):

                # Test that we can get the user credentials cache path for Windows.
                self.assertEqual(
                    get_local_app_config_path(cache_dirname="cache", user_credentials_filename="user_credentials.json"),
                    "/path/to/app/data/cache/user_credentials.json",
                )

        # Test that we can get it on any other system. Note that this assumes we're running these unittests on a
        # non-Windows system.
        with mock.patch("myst_v1alpha1.utils.auth_utils.os.path.expanduser") as os_path_expanduser_patch:
            os_path_expanduser_patch.return_value = "/Users/user"
            self.assertEqual(
                get_local_app_config_path(cache_dirname="cache", user_credentials_filename="user_credentials.json"),
                "/Users/user/.config/cache/user_credentials.json",
            )

    def test_load_user_credentials(self):
        # Create a mock user credentials file to test with.
        temp_user_credentials_filepath = tempfile.mktemp()
        with open(temp_user_credentials_filepath, "w") as temp_user_credentials_file:
            mock_user_credentials_json = {
                "refresh_token": "mock_refresh_token",
                "id_token": "mock_id_token",
                "token_uri": "mock_token_uri",
                "client_id": "mock_client_id",
                "client_secret": "mock_client_secret",
                "scopes": ["mock_scope"],
            }
            json.dump(mock_user_credentials_json, temp_user_credentials_file)

        # Test that we can load user credentials.
        user_credentials = load_user_credentials(user_credentials_path=temp_user_credentials_filepath)

        # Test that the user credentials was loaded as expected.
        self.assertIsInstance(user_credentials, google.oauth2.credentials.Credentials)
        self.assertEqual(user_credentials.refresh_token, "mock_refresh_token")
        self.assertEqual(user_credentials.id_token, "mock_id_token")
        self.assertEqual(user_credentials.token_uri, "mock_token_uri")
        self.assertEqual(user_credentials.client_id, "mock_client_id")
        self.assertEqual(user_credentials.client_secret, "mock_client_secret")
        self.assertEqual(user_credentials.scopes, ["mock_scope"])

    def test_save_user_credentials(self):
        # Create a temporary file path and some mock user credentials to test with.
        temp_user_credentials_filepath = tempfile.mktemp()
        user_credentials = google.oauth2.credentials.Credentials(
            token=None,
            refresh_token="mock_refresh_token",
            id_token="mock_id_token",
            token_uri="mock_token_uri",
            client_id="mock_client_id",
            client_secret="mock_client_secret",
            scopes=["mock_scope"],
        )

        # Test that we're returned the user credentials filepath.
        self.assertEqual(
            save_user_credentials(user_credentials=user_credentials, target_path=temp_user_credentials_filepath),
            temp_user_credentials_filepath,
        )

        # Test that we successfully wrote the user credentials.
        self.assertTrue(os.path.exists(temp_user_credentials_filepath))

        # Test that the contents of the user credentials were written as expected.
        with open(temp_user_credentials_filepath, "r") as temp_user_credentials_file:
            user_credentials_json = json.load(temp_user_credentials_file)
            self.assertEqual(
                user_credentials_json,
                {
                    "refresh_token": "mock_refresh_token",
                    "id_token": "mock_id_token",
                    "token_uri": "mock_token_uri",
                    "client_id": "mock_client_id",
                    "client_secret": "mock_client_secret",
                    "scopes": ["mock_scope"],
                },
            )
