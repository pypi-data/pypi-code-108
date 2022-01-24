from functools import wraps

import requests
from pydantic.types import UUID4
from taktile_client.config import collect_api_key

from tktl.core.config import set_api_key, settings
from tktl.core.loggers import LOG
from tktl.core.strings import CLIStrings, HeaderStrings


def login(api_key=None):
    """

    Parameters
    ----------
    api_key

    Returns
    -------

    """
    if api_key is None:
        LOG.error("Authentication failed: no key provided")
        return False
    try:
        UUID4(api_key)
    except ValueError:
        LOG.error("Authentication failed: Key format is invalid")
        return False
    set_api_key(api_key)
    return True


def logout():
    set_api_key(None)
    return True


def validate_key(suppress=False, api_key=None):
    if not api_key:
        api_key = collect_api_key()
    if not api_key:
        LOG.error(CLIStrings.AUTH_ERROR_MISSING_KEY)
        return False

    r = requests.get(
        f"{settings.TAKTILE_API_URL}{settings.API_V1_STR}/users/me",
        headers={"Accept": HeaderStrings.APPLICATION_JSON, "X-Api-Key": api_key},
    )
    try:
        r.raise_for_status()
    except requests.exceptions.RequestException:
        LOG.error(f'Request failed: {r.json()["detail"]}')
        return False

    if not suppress:
        LOG.log("Login successful!", color="green")
    return True


def validate_decorator(func):
    @wraps(func)
    def wrapped_validation(*args, **kwargs):
        if not validate_key(suppress=True):
            return
        return func(*args, **kwargs)

    return wrapped_validation
