"""Implements support for anonymous users: temporary, short-lived accounts that can be used to quickly evaluate Terality.

For any regular usage, creating a full-fledged Terality account is required.
"""

import datetime as dt

from common_client_scheduler.responses import CreateAnonymousUserResponse

from terality._terality.client import anonymous_client
from terality._terality.globals import load_global_client
from terality._terality.utils.account import (
    has_valid_terality_config_file,
    has_valid_terality_credentials_file,
)
from terality._terality.utils.config import TeralityConfig, TeralityCredentials


def create_anonymous_user():
    """Get started with Terality without any setup: create a temporary Terality account on this machine.

    This method should only be used when evaluating Terality. For any real usage, please create a permanent
    Terality account at https://app.terality.com.

    The account created by this quickstart method has a limited duration, after which all data in this
    account will be deleted. This quickstart account also has a lower data cap than a normal account, and
    can't be upgraded.

    When the lifetime of the quickstart account is exceeded, further calls to Terality will return errors.
    """
    if has_valid_terality_config_file() or has_valid_terality_credentials_file():
        # Note that we don't detect if the previous configuration is for a quickstart account or not.
        # This means that a user that used the quickstart method on this laptop then created a real account
        # with `terality account create` will be greeted with a "configuration files already exist" warning.
        print(
            "Terality is already configured on this machine, will not create an anonymous account."
        )
        return

    client = anonymous_client()
    res = client.poll_for_answer("anonymous_users", payload={})
    if not isinstance(res, CreateAnonymousUserResponse):
        raise ValueError(
            f"Unexpected server answer: expected type 'CreateAnonymousUserResponse', got '{type(res)}'"
        )
    user_id = res.user_id
    api_key = res.api_key
    expires_at = res.expires_at
    _write_terality_configuration(user_id, api_key)

    print(
        f"Terality is now initialized on this machine. This is a temporary demonstration account that will only remain valid for {_format_account_duration_in_minutes(expires_at)} minutes. To create a full account, please go to https://app.terality.com (it's free!)."
    )


def _write_terality_configuration(email: str, api_key: str):
    credentials = TeralityCredentials(user_id=email, user_password=api_key)
    credentials.save()
    config = TeralityConfig()
    config.save()

    load_global_client()


def _format_account_duration_in_minutes(expires_at: dt.datetime) -> str:
    return str(round(max((expires_at - dt.datetime.utcnow()).total_seconds() // 60, 0)))
