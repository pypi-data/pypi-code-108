"""This module contains utility functions related to caching."""
import json
import os

import google.oauth2.credentials

from myst_v1alpha1.utils.core_utils import make_directory


def get_local_app_config_path(cache_dirname, user_credentials_filename):
    """Gets the default path to the local user credentials cache.

    Args:
        cache_dirname (str): name of cache dir
        user_credentials_filename (str): name of file storing cached user credentials

    Returns:
        user_credentials_cache_path (str): path to user credentials cache file
    """

    if os.name == "nt":  # needed for Windows.
        config_path = os.environ["APPDATA"]
    else:
        config_path = os.path.join(os.path.expanduser("~"), ".config")

    config_path = os.path.join(config_path, cache_dirname)
    user_credentials_cache_path = os.path.join(config_path, user_credentials_filename)
    return user_credentials_cache_path


def load_user_credentials(user_credentials_path):
    """Loads user credentials from a file.

    Args:
        user_credentials_path (str): full path to user credentials file

    Returns:
        user_credentials (google.oauth2.credentials.Credentials): user credentials loaded from file
    """
    with open(user_credentials_path, "r") as user_credentials_file:
        user_credentials_json = json.load(user_credentials_file)

    # Note that we don't save the OAuth 2.0 access token, so we're explicitly passing it in here.
    user_credentials = google.oauth2.credentials.Credentials(token=None, **user_credentials_json)
    return user_credentials


def save_user_credentials(user_credentials, target_path):
    """Saves user credentials to a file.

    Args:
        user_credentials (google.oauth2.credentials.Credentials): user credentials to save
        target_path (str): full path to file to save user credentials to

    Returns:
        target_path (str): full path to user credentials file
    """
    cache_dir = os.path.dirname(target_path)
    make_directory(cache_dir)
    with open(target_path, "w") as cache_file:

        # Note that we don't save the OAuth 2.0 access token, so we're explicitly not passing it in here.
        user_credentials_json = {
            "refresh_token": user_credentials.refresh_token,
            "id_token": user_credentials.id_token,
            "token_uri": user_credentials.token_uri,
            "client_id": user_credentials.client_id,
            "client_secret": user_credentials.client_secret,
            "scopes": user_credentials.scopes,
        }
        json.dump(user_credentials_json, cache_file)

    return target_path
