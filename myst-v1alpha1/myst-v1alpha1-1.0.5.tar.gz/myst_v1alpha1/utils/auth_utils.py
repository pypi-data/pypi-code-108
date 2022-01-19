import os

from google.oauth2.service_account import IDTokenCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

import myst_v1alpha1
from myst_v1alpha1.constants import MYST_APPLICATION_CREDENTIALS_ENVIRONMENT_VARIABLE
from myst_v1alpha1.user_credentials_cache import UserCredentialsCache
from myst_v1alpha1.utils.core_utils import get_pkg_resource_path


def create_bearer_authorization_header(token):
    """Creates a Bearer (a.k.a. Token) Authorization header.

    Args:
        token (str): bearer authorization JSON Web Token (jwt)

    Returns:
        header (dict): authorization header
    """
    header = {"Authorization": "Bearer {}".format(token)}
    return header


def get_service_account_credentials(service_account_key_file_path=None):
    """Gets credentials from a service account key file.

    Args:
        service_account_key_file_path (str, optional): full path to the service account's private key file; if none is
            specified, this method fall backs to getting the path from the environment

    Returns:
        credentials (google.oauth2.service_account.IDTokenCredentials): Google OAuth 2.0 credentials identifying the
            service account
    """
    if service_account_key_file_path is None:
        service_account_key_file_path = os.getenv(MYST_APPLICATION_CREDENTIALS_ENVIRONMENT_VARIABLE)

    # Make sure that the service account key file was passed explicitly or found in the environment.
    if service_account_key_file_path is None:
        raise ValueError(
            str.format(
                "Either explicitly pass in the full path to your service account key file using "
                "`myst_v1alpha1.authenticate(use_service_account=True, service_account_key_file_path='<path>')` "
                "or set `{MYST_APPLICATION_CREDENTIALS_ENVIRONMENT_VARIABLE}` to the full path in your environment..",
                MYST_APPLICATION_CREDENTIALS_ENVIRONMENT_VARIABLE=MYST_APPLICATION_CREDENTIALS_ENVIRONMENT_VARIABLE,
            )
        )

    credentials = IDTokenCredentials.from_service_account_file(
        filename=service_account_key_file_path, target_audience=myst_v1alpha1.api_host
    )
    return credentials


def get_user_credentials(use_console=False, read_from_cache=True, write_to_cache=True):
    """Gets credentials from the current user by prompting the user to authorize and perform a Google OAuth 2.0 flow.

    Note that this will first try to grab the credentials from the local cache and if that doesn't work, will
    perform the whole OAuth 2.0 dance with Google's OAuth 2.0 service to fetch new credentials.

    Args:
        use_console (bool, optional): whether to use the console instead of opening and using a web browser
        read_from_cache (bool, optional): whether or not to first try to read the user credentials from the cache
        write_to_cache (bool, optional): whether or not to write user credentials back to cache

    Returns:
        user_credentials (google.oauth2.credentials.Credentials): Google OAuth 2.0 credentials identifying current user
    """
    # Get the default global user credentials cache.
    user_credentials_cache = UserCredentialsCache()

    if read_from_cache:
        # Note that this will also return `None` if user credentials were not found or couldn't be loaded from cache.
        user_credentials = user_credentials_cache.load()
    else:
        user_credentials = None

    if user_credentials is None:

        # Couldn't find user credentials in cache or explicitly told not to use cache, so perform the OAuth2.0 dance.
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file=get_pkg_resource_path("google_oauth_client_not_so_secret.json"),
            scopes=["openid", "https://www.googleapis.com/auth/userinfo.email"],
        )
        user_credentials = flow.run_console() if use_console else flow.run_local_server()

        # Write newly fetched user credentials to cache.
        if write_to_cache:
            user_credentials_cache.save(user_credentials=user_credentials)

    return user_credentials


def get_credentials(use_service_account=False, use_console=False, service_account_key_file_path=None):
    """Gets credentials from the environment.

    Args:
        use_service_account (bool, optional): whether or not to use service account instead of end-user credentials;
            if this is `True` and `service_account_key_file_path` isn't given, this will look for the key file path
            in the `MYST_APPLICATION_CREDENTIALS` environment variable
        use_console (bool, optional): whether or not to use the console for the user account authorization flow
        service_account_key_file_path (str, optional): full path to service account key file; if this is given,
            `use_service_account` is inferred to be `True`

    Returns:
        credentials (google.oauth2.credentials.Credentials): Google OAuth 2.0 credentials identifying current user or
            service account
    """
    # Validate arguments.
    if use_service_account and use_console:
        raise ValueError("Both `use_service_account` and `use_console` can not be `True`.")

    if use_console and service_account_key_file_path:
        raise ValueError("`service_account_key_file_path` was specified but `use_console` is set to `True`.")

    # Get credentials using desired method.
    if use_service_account or service_account_key_file_path is not None:
        credentials = get_service_account_credentials(service_account_key_file_path=service_account_key_file_path)
    else:
        credentials = get_user_credentials(use_console=use_console, read_from_cache=True, write_to_cache=True)
    return credentials


def clear_user_credentials_cache():
    """Clears the local user credentials cache."""
    user_credentials_cache = UserCredentialsCache()
    user_credentials_cache.clear()


def authenticate(credentials=None, use_service_account=False, use_console=False, service_account_key_file_path=None):
    """Authenticates user and sets global `client` that can be used to make authenticated requests.

    Args:
        credentials (google.auth.credentials.Credentials, optional): custom credentials to use instead of getting
            credentials from user or service account
        use_service_account (bool, optional): whether or not to use service account instead of end-user credentials;
            if this is `True` and `service_account_key_file_path` isn't given, this will look for the key file path
            in the `MYST_APPLICATION_CREDENTIALS` environment variable
        use_console (bool, optional): whether or not to use the console for the user account authorization flow
        service_account_key_file_path (str, optional): full path to service account key file; if this is given,
            `use_service_account` is inferred to be `True`
    """
    client = myst_v1alpha1.get_client()
    credentials = credentials or get_credentials(
        use_service_account=use_service_account,
        use_console=use_console,
        service_account_key_file_path=service_account_key_file_path,
    )
    client.authenticate(credentials=credentials)
