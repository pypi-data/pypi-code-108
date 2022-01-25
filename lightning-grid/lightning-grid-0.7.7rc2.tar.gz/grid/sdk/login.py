import json
import os
from pathlib import Path
from typing import Optional

from grid.sdk._gql.queries import get_grid_user_id
from grid.sdk.auth import Credentials
from grid.sdk import env
from grid.sdk.api import list_clusters
from grid.sdk.client.grid_gql import gql_client
from grid.sdk.user import set_default_cluster


def login(
    username: Optional[str] = None,
    user_id: Optional[str] = None,
    api_key: Optional[str] = None,
    *,
    _url=env.GRID_URL  # noqa - For testing purposes only. not user facing.
):
    """
    Log in with your grid.ai credentials for usage of the SDK in the running process.

    All parameters are optional. Calling ``login()`` without parameters will check if
    the ``GRID_USER_ID`` and ``GRID_API_KEY`` env vars have been set (using those if
    available), otherwise it will check for the file ``credentials.json`` in the
    machines ``$HOME/.grid`` directory (if it exists).

    If no credentials have been stored, then you must pass in your API key and either
    your username or user id (if you know it). Your user id and API key can be found
    by navigating to https://platform.grid.ai/#/settings?tabId=apikey.

    Parameters
    ----------
    username
        your grid username. This is either be your github username or email address,
        depending on what you use when signing into the grid platform at:
        https://platform.grid.ai

    user_id
        Your grid user id. This can be found by visiting https://platform.grid.ai/#/settings?tabId=apikey.
    api_key
        Your grid API key. This can be found by visiting https://platform.grid.ai/#/settings?tabId=apikey.
    """
    if user_id and api_key:
        creds = Credentials(user_id=user_id, api_key=api_key)
        _create_credentials_file(creds)
    elif username and api_key:
        creds = Credentials(user_id=username, api_key=api_key)
        client = gql_client(url=_url + "/graphql", creds=creds)
        user_id = get_grid_user_id(client=client)
        creds = Credentials(user_id=user_id, api_key=api_key)
        _create_credentials_file(creds)
    elif (username or user_id) or api_key:
        raise ValueError("Either (`user_id` OR `username`) AND `api_key` need to be set, or none set.")
    else:
        creds = Credentials.from_locale()

    # adding context to the user settings
    # this will overwrite the context user set - when we have the set context command.
    # solution to that problem is to have DEFAULT_CONTEXT and SELECTED_CONTEXT
    cluster_list = list_clusters(is_global=True)
    default_cluster = cluster_list.default_cluster
    set_default_cluster(cluster_id=default_cluster)

    settings_path = Path(env.GRID_SETTINGS_PATH)
    user_settings = json.load(settings_path.open())
    user_settings['grid_url'] = _url
    with settings_path.open('w') as file:
        json.dump(user_settings, file, ensure_ascii=False, indent=4)

    # resetting the env variables
    os.environ['GRID_USER_ID'] = creds.user_id
    os.environ['GRID_API_KEY'] = creds.api_key
    os.environ['GRID_URL'] = _url
    os.environ['GRID_CLUSTER_ID'] = default_cluster
    env.reset_global_variables()

    creds = Credentials.from_locale()
    # warmup cache. can take ~2 sec on first call
    _ = gql_client(url=_url + '/graphql', creds=creds)
    return True


def _create_credentials_file(creds: Credentials):
    Path(env.GRID_CREDENTIAL_PATH).parent.mkdir(parents=True, exist_ok=True)
    with Path(env.GRID_CREDENTIAL_PATH).open('w') as file:
        json.dump({'UserID': creds.user_id, 'APIKey': creds.api_key}, file, ensure_ascii=False, indent=4)
