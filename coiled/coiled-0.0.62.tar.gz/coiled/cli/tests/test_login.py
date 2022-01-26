import os
from unittest import mock

import dask
import pytest
from click.testing import CliRunner
from coiled.cli.login import login
from coiled.utils import normalize_server
from django.test import override_settings

pytestmark = pytest.mark.skipif(
    os.environ.get("TEST_BACKEND", "in_process") == "aws", reason="unknown"
)


@pytest.mark.skipif(
    not all(
        (
            os.environ.get("AWS_SECRET_ACCESS_KEY", None),
            os.environ.get("AWS_ACCESS_KEY_ID", None),
        )
    ),
    reason="Mocking user home directory breaks ~/.aws/credentials",
)
def test_login(sample_user, tmp_path, sample_user_token):
    with mock.patch("os.path.expanduser") as mock_expanduser:
        mock_expanduser.return_value = str(tmp_path)
        token = sample_user_token
        server = dask.config.get("coiled.server")
        server = normalize_server(server)

        runner = CliRunner()
        result = runner.invoke(login, input=token)

        # Test output of command
        assert result.exit_code == 0
        assert "login" in result.output
        assert server in result.output
        assert "saved" in result.output

        # Ensure credentials were saved to config file
        config_file = os.path.join(tmp_path, ".config", "dask", "coiled.yaml")
        [config] = dask.config.collect_yaml([config_file])
        assert config["coiled"]["user"] == sample_user.user.username
        assert config["coiled"]["token"] == token
        assert config["coiled"]["server"] == server


@pytest.mark.skipif(
    not all(
        (
            os.environ.get("AWS_SECRET_ACCESS_KEY", None),
            os.environ.get("AWS_ACCESS_KEY_ID", None),
        )
    ),
    reason="Mocking user home directory breaks ~/.aws/credentials",
)
def test_login_token_input(sample_user, tmp_path, sample_user_token):
    with mock.patch("os.path.expanduser") as mock_expanduser:
        mock_expanduser.return_value = str(tmp_path)
        token = sample_user_token
        server = dask.config.get("coiled.server")
        server = normalize_server(server)

        runner = CliRunner()
        result = runner.invoke(login, args=f"--token {token}")

        # Test output of command
        assert result.exit_code == 0
        assert "saved" in result.output

        # Ensure credentials were saved to config file
        config_file = os.path.join(tmp_path, ".config", "dask", "coiled.yaml")
        [config] = dask.config.collect_yaml([config_file])
        assert config["coiled"]["user"] == sample_user.user.username
        assert config["coiled"]["token"] == token
        assert config["coiled"]["server"] == server


def test_login_bad_token_asks_login_again(sample_user, tmp_path, sample_user_token):
    runner = CliRunner()
    stdin = [
        "not-a-valid-token",  # Log in with bad token
        sample_user_token,  # Log in with good token
        "n",  # Don't have credentials
    ]
    result = runner.invoke(login, input="\n".join(stdin))

    assert result.exit_code == 0
    output = result.output.lower()
    assert "invalid coiled token" in output
    # Asked to login twice, once with bad token and once with good token
    assert output.count("please login") == 2


@override_settings(LONG_LIVED_TOKENS_ENABLED=True)
def test_login_new_token(sample_user, long_lived_token_for_sample_user):
    runner = CliRunner()
    stdin = [
        long_lived_token_for_sample_user,
    ]
    result = runner.invoke(login, input="\n".join(stdin))
    print(result.output)
    assert "Authentication successful" in result.output
    assert "Credentials have been saved" in result.output
    assert result.exit_code == 0


def test_login_no_retry(sample_user, tmp_path):
    # Ensure that when `coiled login --no-retry` raises an expection when an
    # invalid token is given instead of asking for a different token
    runner = CliRunner()
    result = runner.invoke(login, args="--no-retry", input="not-a-valid-token\n")

    assert result.exit_code != 0
    assert result.exception
    assert "invalid token" in str(result.exception).lower()


def test_login_bad_account(sample_user, tmp_path, sample_user_token):
    runner = CliRunner()
    token = sample_user_token
    result = runner.invoke(login, [f"-t {token}", "-a CaptainAmerica"])
    assert result.exit_code != 0
    assert result.exception
    assert "Bad account format" in str(result.exception)
