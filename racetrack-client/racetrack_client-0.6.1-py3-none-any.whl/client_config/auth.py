import requests
import logging

from racetrack_client.client_config.alias import resolve_lifecycle_url
from racetrack_client.client_config.client_config import ClientConfig
from racetrack_client.utils.request import parse_response


class AuthError(RuntimeError):
    def __init__(self, cause: str):
        super().__init__()
        self.cause = cause

    def __str__(self):
        return f'authentication error: {self.cause}'


def set_user_auth(client_config: ClientConfig, lifecycle_url: str, user_auth: str):
    """
    You need to save the resulting config if you want to make changes persist
    """
    lifecycle_url = resolve_lifecycle_url(client_config, lifecycle_url)

    if len(user_auth) == 0:
        if lifecycle_url in client_config.user_auths:
            del client_config.user_auths[lifecycle_url]
        else:
            raise RuntimeError(f'Missing {lifecycle_url} in Racetrack logged servers')
    else:
        client_config.user_auths[lifecycle_url] = user_auth


def get_user_auth(client_config: ClientConfig, lifecycle_url: str) -> str:
    if lifecycle_url in client_config.user_auths:
        return client_config.user_auths[lifecycle_url]

    if is_auth_required(lifecycle_url):
        raise AuthError(f"missing login. You need to do: racetrack login {lifecycle_url} <token>")

    return ''


def is_auth_required(lifecycle_url: str) -> bool:
    r = requests.get(
        f'{lifecycle_url}/health',
        verify=False,
    )
    response = parse_response(r, 'Lifecycle response error')
    return response["auth_required"]
