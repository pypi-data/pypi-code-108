import json
import tempfile
from unittest.mock import Mock, patch

import click
import pytest

import anyscale
from anyscale.authenticate import AuthenticationBlock
from anyscale.client.openapi_client.rest import ApiException as ApiExceptionInternal
import anyscale.conf


def test_load_credentials_env_var(monkeypatch):
    """
    Test credentials loaded from environment variable even when credentials exist in file.
    """
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock", __init__=Mock(return_value=None)
    ):
        auth_api_client = AuthenticationBlock()

    monkeypatch.setenv("ANYSCALE_CLI_TOKEN", "sss_os_environ")
    with tempfile.NamedTemporaryFile("w") as temp_credentials_file:
        temp_credentials_file.write(json.dumps({"cli_token": "sss_file_credential"}))
        temp_credentials_file.flush()
        anyscale.authenticate.CREDENTIALS_FILE = temp_credentials_file.name
        assert auth_api_client._load_credentials() == (
            "sss_os_environ",
            "ANYSCALE_CLI_TOKEN",
        )


def test_load_credentials_file(monkeypatch):
    """
    Test credentials loaded from file when credentials don't exist in environment variable.
    """
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock", __init__=Mock(return_value=None)
    ):
        auth_api_client = AuthenticationBlock()

    monkeypatch.delenv("ANYSCALE_CLI_TOKEN", raising=False)
    with tempfile.NamedTemporaryFile("w") as temp_credentials_file:
        temp_credentials_file.write(json.dumps({"cli_token": "sss_file_credential"}))
        temp_credentials_file.flush()
        anyscale.authenticate.CREDENTIALS_FILE = temp_credentials_file.name
        assert auth_api_client._load_credentials() == (
            "sss_file_credential",
            anyscale.authenticate.CREDENTIALS_FILE,
        )


def test_validate_credentials_format() -> None:
    """
    Test credentials are of the correct format.
    """
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock", __init__=Mock(return_value=None)
    ):
        auth_api_client = AuthenticationBlock()

    with pytest.raises(click.ClickException):
        auth_api_client._validate_credentials_format("abc")

    with pytest.raises(click.ClickException):
        auth_api_client._validate_credentials_format("")

    # Should not raise an exception.
    auth_api_client._validate_credentials_format("sss_abcdefghjijklmnop")


def test_validate_api_client_auth() -> None:
    """
    Test credentials are validated with by calling /api/v2/userinfo.
    """
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock", __init__=Mock(return_value=None)
    ):
        auth_api_client = AuthenticationBlock()

    # Test credentials are validated when /api/v2/userinfo returns successful response.
    auth_api_client.api_client = Mock()
    auth_api_client._validate_api_client_auth()

    # Test error is raised when /api/v2/userinfo returns 401 not authenticated response.
    auth_api_client.api_client.get_user_info_api_v2_userinfo_get = Mock(
        side_effect=ApiExceptionInternal(status=401)
    )
    with pytest.raises(click.ClickException):
        auth_api_client._validate_api_client_auth()
