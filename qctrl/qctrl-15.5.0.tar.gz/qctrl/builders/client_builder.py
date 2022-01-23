# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring

import json
import logging
import os
from pathlib import Path
from typing import (
    Callable,
    Dict,
    Tuple,
    Union,
)
from urllib.parse import urljoin

import jwt
from gql import Client
from qctrlcommons.auth import (
    BearerTokenAuth,
    ClientAuthBase,
)
from qctrlcommons.exceptions import QctrlException
from qctrlcommons.utils import generate_user_agent

from qctrl.builders.http_transport import (
    QctrlGqlClient,
    QctrlRequestsHTTPTransport,
)
from qctrl.utils import check_client_version

from .. import __version__ as qctrl_version
from ..queries import (
    CreateTokenQuery,
    RefreshTokenQuery,
)
from ..scripts_utils import (
    file_path_for_url,
    interactive_authentication,
    write_auth_file,
)

LOGGER = logging.getLogger(__name__)


def _valid_refresh_token(refresh_token: str) -> bool:
    """
    Verify refresh_token signature to ensure it can be used without requiring
    new credentials.
    """
    try:
        jwt.decode(
            refresh_token, options={"verify_signature": False, "verify_exp": True}
        )
        return True
    except jwt.InvalidTokenError:
        return False


def get_jwt_token(api_root: str) -> Tuple[str, str, Callable]:
    """Get Jwt token from file storage.

    Parameters
    ----------
    api_root : str
        Root url of the api.


    Returns
    -------
    tuple
        access_token, refresh_token, token_observer

    """
    file_path = _credentials_file_path(api_root)
    access_token, refresh_token = _parse_credentials_file(file_path)

    if not _valid_refresh_token(refresh_token):
        file_path = _credentials_file_path(api_root, force_authentication=True)
        access_token, refresh_token = _parse_credentials_file(file_path)

    def token_observer(tokens):
        return write_auth_file(
            tokens["access_token"], tokens["refresh_token"], file_path=file_path
        )

    return access_token, refresh_token, token_observer


def _parse_credentials_file(file_path: Union[str, Path]) -> tuple:
    """Parses a credentials file and returns a tuple of (access_token,
    refresh_token) to be used for login.

    Parameters
    ----------
    file_path: str
        The location of the credentials file to parse.


    Returns
    -------
    tuple
        access_token, refresh_token

    Raises
    ------
    OSError
        if credentials file does not exist
    """

    if not os.path.isfile(file_path):
        raise OSError(f"credentials file does not exist: {file_path}")

    # get data
    with open(file_path, encoding="utf-8") as json_file:
        data = json_file.read()
        data = json.loads(data)

    return data["access_token"], data["refresh_token"]


def _credentials_file_path(api_root: str, force_authentication: bool = False) -> Path:

    env_file_path = os.environ.get("QCTRL_AUTHENTICATION_CREDENTIALS", "")

    if env_file_path:
        file_path = Path(env_file_path)
    else:
        file_path = file_path_for_url(api_root)

    if not file_path.exists() or force_authentication:
        gql_annonymous_client = create_gql_client(api_root)
        create_token_client = CreateTokenQuery(gql_annonymous_client)
        interactive_authentication(client=create_token_client, api_root=api_root)

    return file_path


def create_client_auth(
    api_root: str, email: str = None, password: str = None
) -> BearerTokenAuth:
    """
    Returns the GQL client.

    Parameters
    ----------
    api_root: str
        The Api url the package should use.
    email: str
        (Default value = None)
    password: str
        (Default value = None)

    Returns
    -------
    BearerTokenAuth
        Object to handle authentication in the GQL Client.

    Raises
    ------
    QctrlException
        if input is missing email or password.
    """

    gql_annonymous_client = create_gql_client(api_root)
    create_token_query = CreateTokenQuery(gql_annonymous_client)
    refresh_token_query = RefreshTokenQuery(gql_annonymous_client)

    if email or password:
        if email is None:
            raise QctrlException("email is required.")

        if password is None:
            raise QctrlException("password is required.")

        access_token, refresh_token = create_token_query(email, password)
        auth = BearerTokenAuth(access_token, refresh_token, refresh_token_query)

    # via interactive mode or local file if there's no arguments provided by user
    else:
        access_token, refresh_token, token_observer = get_jwt_token(api_root)
        auth = BearerTokenAuth(
            access_token, refresh_token, refresh_token_query, token_observer
        )

    return auth


@check_client_version
def create_gql_client(
    api_root: str, auth: ClientAuthBase = None, headers: Dict = None
) -> Client:
    """Creates a gql client.

    Parameters
    ----------
    auth: ClientAuthBase
        The auth object.
    api_root: str
        The host url.
    headers: Dict
        HTTP headers


    Returns
    -------
    Client
        The GQL Client.
    """

    url = urljoin(api_root, "graphql/")
    LOGGER.debug("gql url: %s", url)
    headers = headers or {}

    headers.update(
        {
            "Content-Encoding": "gzip",
            "Content-Type": "application/json",
            "User-Agent": generate_user_agent("Q-CTRL Python", version=qctrl_version),
        }
    )

    # use_json needs to be set to false otherwise the library will attempt
    # to dump and encode the data twice.
    transport = QctrlRequestsHTTPTransport(
        url=url, use_json=False, headers=headers, auth=auth, retries=3
    )
    return QctrlGqlClient(transport=transport, fetch_schema_from_transport=True)
