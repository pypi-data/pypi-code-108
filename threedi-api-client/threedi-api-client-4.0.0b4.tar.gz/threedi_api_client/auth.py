from datetime import datetime, timedelta

import jwt

from .openapi import ApiClient, Authenticate, Configuration, V3Api
from .versions import host_remove_version

# Get new token REFRESH_TIME_DELTA before it really expires.
REFRESH_TIME_DELTA = timedelta(hours=4).total_seconds()


def get_auth_token(username: str, password: str, api_host: str):
    api_client = ApiClient(
        Configuration(
            username=username, password=password, host=host_remove_version(api_host)
        )
    )
    api = V3Api(api_client)
    return api.auth_token_create(Authenticate(username, password))


def is_token_usable(token: str) -> bool:
    if token is None:
        return False

    try:
        # Get payload without verifying signature,
        # does NOT validate claims (including exp)
        payload = jwt.decode(
            token,
            options={"verify_signature": False},
        )
    except (jwt.exceptions.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return False

    expiry_dt = datetime.utcfromtimestamp(payload["exp"])
    sec_left = (expiry_dt - datetime.utcnow()).total_seconds()
    return sec_left >= REFRESH_TIME_DELTA


def refresh_api_key(config: Configuration):
    """Refreshes the access key if its expired"""
    api_key = config.api_key.get("Authorization")
    if is_token_usable(api_key):
        return

    refresh_key = config.api_key["refresh"]
    if is_token_usable(refresh_key):
        api_client = ApiClient(Configuration(host_remove_version(config.host)))
        api = V3Api(api_client)
        token = api.auth_refresh_token_create({"refresh": config.api_key["refresh"]})
    else:
        token = get_auth_token(config.username, config.password, config.host)
    config.api_key = {"Authorization": token.access, "refresh": token.refresh}
