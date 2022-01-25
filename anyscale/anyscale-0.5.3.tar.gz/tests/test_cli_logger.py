from contextlib import redirect_stderr, redirect_stdout
import io
import os
from unittest.mock import Mock, patch

import click
import pytest

from anyscale.authenticate import get_auth_api_client
from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client.rest import ApiException as ApiExceptionInternal
from anyscale.sdk.anyscale_client.rest import ApiException as ApiExceptionExternal


def test_warning_to_stderr():
    # Test warnings are printed to stderr
    log = BlockLogger()
    f = io.StringIO()
    warning_message = "test_warning"
    with redirect_stderr(f):
        log.warning(warning_message)

    assert warning_message in f.getvalue()


def test_block():
    log = BlockLogger()

    # Test opening block, writing info, closing block
    log.open_block(block_label="block1")
    log.info("msg1", block_label="block1")
    log.close_block(block_label="block1")

    # Test error raised when opening two blocks without closing first
    log.open_block(block_label="block1")
    with pytest.raises(Exception):
        log.open_block(block_label="block2")

    # Test error raised when closing block that wasn't opened
    with pytest.raises(Exception):
        log.close_block(block_label="block2")

    # Test error raised when writing to block that wasn't opened
    with pytest.raises(Exception):
        log.info("msg2", block_label="block2")


def test_debug_env_var():
    log = BlockLogger()
    f = io.StringIO()
    debug_message = "test_debug"

    # Test debug message is not printed to stdout if ANYSCALE_DEBUG != 1
    os.environ.pop("ANYSCALE_DEBUG", None)
    with redirect_stdout(f):
        log.debug(debug_message)
    assert f.getvalue() == ""

    # Test debug message is printed to stdout if ANYSCALE_DEBUG == 1
    os.environ["ANYSCALE_DEBUG"] = "1"
    with redirect_stdout(f):
        log.debug(debug_message)
    assert debug_message in f.getvalue()


def test_format_api_exception_internal():
    # Tests that API exceptions are correctly formatted for the internal API
    BlockLogger()
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock",
        _validate_api_client_auth=Mock(),
        _validate_credentials_format=Mock(),
    ):
        mock_api_client = get_auth_api_client(
            cli_token="fake_cli_token", host="fake_host"
        ).api_client

    # Test non ApiExceptions are not caught by log.format_api_exception
    with patch.multiple(
        "anyscale.api.openapi_client.ApiClient",
        call_api=Mock(side_effect=ZeroDivisionError()),
    ), pytest.raises(ZeroDivisionError):
        mock_api_client.get_project_api_v2_projects_project_id_get("bad_project_id")

    e = ApiExceptionInternal()
    e.headers = Mock(_container={})
    with patch.multiple(
        "anyscale.api.openapi_client.ApiClient", call_api=Mock(side_effect=e),
    ):
        # Test original ApiException is raised if ANYSCALE_DEBUG == 1
        os.environ["ANYSCALE_DEBUG"] = "1"
        with pytest.raises(ApiExceptionInternal):
            mock_api_client.get_project_api_v2_projects_project_id_get("bad_project_id")

        # Test formatted ClickException is raised if ANYSCALE_DEBUG != 1
        os.environ.pop("ANYSCALE_DEBUG", None)
        with pytest.raises(click.ClickException):
            mock_api_client.get_project_api_v2_projects_project_id_get("bad_project_id")


def test_format_api_exception_external():
    # Tests that API exceptions are correctly formatted for the external API
    BlockLogger()
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock",
        _validate_api_client_auth=Mock(),
        _validate_credentials_format=Mock(),
    ):
        mock_api_client = get_auth_api_client(
            cli_token="fake_cli_token", host="fake_host"
        ).anyscale_api_client

    # Test non ApiExceptions are not caught by log.format_api_exception
    with patch.multiple(
        "anyscale.sdk.anyscale_client.ApiClient",
        call_api=Mock(side_effect=ZeroDivisionError()),
    ), pytest.raises(ZeroDivisionError):
        mock_api_client.list_projects()

    e = ApiExceptionExternal()
    e.headers = Mock(_container={})
    with patch.multiple(
        "anyscale.sdk.anyscale_client.ApiClient", call_api=Mock(side_effect=e),
    ):
        # Test original ApiException is raised if ANYSCALE_DEBUG == 1
        os.environ["ANYSCALE_DEBUG"] = "1"
        with pytest.raises(ApiExceptionExternal):
            mock_api_client.list_projects()

        # Test formatted ClickException is raised if ANYSCALE_DEBUG != 1
        os.environ.pop("ANYSCALE_DEBUG", None)
        with pytest.raises(click.ClickException):
            mock_api_client.list_projects()
