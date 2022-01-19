import json
import os
import tempfile
import unittest

import google.oauth2.credentials
import mock

from myst_v1alpha1 import UserCredentialsCache


class UserCredentialsCacheTest(unittest.TestCase):
    @mock.patch("myst_v1alpha1.utils.cache_utils.os.path.expanduser")
    def test_user_credentials_cache(self, os_path_expanduser_patch):
        # Patch user home directory; note that this test assumes that it's running on a non-Windows system.
        os_path_expanduser_patch.return_value = "/Users/user"

        # Test initialize a user credentials cache with the default dirname and user credentials filename.
        user_credentials_cache = UserCredentialsCache()
        self.assertEqual(user_credentials_cache._path, "/Users/user/.config/myst/myst_user_credentials.json")

        # Test that we can also pass in a custom dirname and user credentials filename.
        user_credentials_cache = UserCredentialsCache(
            dirname="cache", user_credentials_filename="user_credentials.json"
        )
        self.assertEqual(user_credentials_cache._path, "/Users/user/.config/cache/user_credentials.json")

    @mock.patch("myst_v1alpha1.user_credentials_cache.get_local_app_config_path")
    def test_user_credentials_cache_load(self, get_user_credentials_cache_path_patch):
        # Patch the user credentials cache path so we don't actually build it based on the current user.
        temp_user_credentials_filepath = tempfile.mktemp()
        get_user_credentials_cache_path_patch.return_value = temp_user_credentials_filepath

        user_credentials_cache = UserCredentialsCache()

        # Test that if the credentials don't exist yet, we just return `None`.
        self.assertIsNone(user_credentials_cache.load())

        # Write a mock user credentials to load.
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

        user_credentials = user_credentials_cache.load()

        # Test that the user credentials was loaded as expected.
        self.assertIsInstance(user_credentials, google.oauth2.credentials.Credentials)
        self.assertEqual(user_credentials.refresh_token, "mock_refresh_token")
        self.assertEqual(user_credentials.id_token, "mock_id_token")
        self.assertEqual(user_credentials.token_uri, "mock_token_uri")
        self.assertEqual(user_credentials.client_id, "mock_client_id")
        self.assertEqual(user_credentials.client_secret, "mock_client_secret")
        self.assertEqual(user_credentials.scopes, ["mock_scope"])

    @mock.patch("myst_v1alpha1.user_credentials_cache.get_local_app_config_path")
    def test_user_credentials_cache_save(self, get_user_credentials_cache_path_patch):
        # Patch the user credentials cache path so we don't actually build it based on the current user.
        temp_user_credentials_filepath = tempfile.mktemp()
        get_user_credentials_cache_path_patch.return_value = temp_user_credentials_filepath

        user_credentials_cache = UserCredentialsCache()

        # Create a mock user credentials object to test with.
        user_credentials = google.oauth2.credentials.Credentials(
            token=None,
            refresh_token="mock_refresh_token",
            id_token="mock_id_token",
            token_uri="mock_token_uri",
            client_id="mock_client_id",
            client_secret="mock_client_secret",
            scopes=["mock_scope"],
        )

        user_credentials_cache.save(user_credentials=user_credentials)

        # Test that we successfully saved the user credentials.
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
