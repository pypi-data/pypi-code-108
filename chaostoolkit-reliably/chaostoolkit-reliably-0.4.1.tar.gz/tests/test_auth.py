import uuid
from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock, patch

import pytest
import yaml
from chaoslib.exceptions import ActivityFailed
from yaml.error import YAMLError

from chaosreliably import get_auth_info


def test_using_config_file() -> None:
    with NamedTemporaryFile(mode="w") as f:
        yaml.safe_dump(
            {
                "auths": {"reliably.com": {"token": "12345", "username": "jane"}},
                "currentOrg": {"name": "test-org"},
            },
            f,
            indent=2,
            default_flow_style=False,
        )
        f.seek(0)

        auth_info = get_auth_info({"reliably_config_path": f.name})
        assert auth_info["token"] == "12345"
        assert auth_info["host"] == "reliably.com"
        assert auth_info["org"] == "test-org"


@patch("chaosreliably.yaml.safe_load")
def test_invalid_yaml_file_errors(mock_safe_load: MagicMock) -> None:
    mock_safe_load.side_effect = YAMLError("An Error")
    with NamedTemporaryFile(mode="w") as f:
        f.write("")
        f.seek(0)
        with pytest.raises(ActivityFailed) as ex:
            get_auth_info({"reliably_config_path": f.name})
    assert str(ex.value) == (
        f"Failed parsing Reliably configuration at '{f.name}': An Error"
    )


def test_using_config_file_but_override_token_and_host() -> None:
    with NamedTemporaryFile(mode="w") as f:
        yaml.safe_dump(
            {
                "auths": {"reliably.com": {"token": "12345", "username": "jane"}},
                "currentOrg": {"name": "test-org"},
            },
            f,
            indent=2,
            default_flow_style=False,
        )
        f.seek(0)

        auth_info = get_auth_info(
            {"reliably_config_path": f.name},
            {"token": "78890", "host": "api.reliably.dev", "org": "overriden-org"},
        )
        assert auth_info["token"] == "78890"
        assert auth_info["host"] == "api.reliably.dev"
        assert auth_info["org"] == "overriden-org"


def test_using_secret_only() -> None:
    auth_info = get_auth_info(
        None, {"token": "78890", "host": "reliably.dev", "org": "secret-org"}
    )
    assert auth_info["token"] == "78890"
    assert auth_info["host"] == "reliably.dev"
    assert auth_info["org"] == "secret-org"


def test_missing_token_from_secrets() -> None:
    with pytest.raises(ActivityFailed) as ex:
        get_auth_info(
            {
                "reliably_config_path": "",
            },
            {"host": "reliably.dev", "org": "an-org"},
        )
    assert str(ex.value) == (
        "Make sure to provide the Reliably token as a secret or via the Reliably's"
        " configuration's file."
    )


def test_missing_host_from_secrets() -> None:
    with pytest.raises(ActivityFailed) as ex:
        get_auth_info(
            {
                "reliably_config_path": "",
            },
            {"token": "78890", "org": "an-org"},
        )
    assert str(ex.value) == (
        "Make sure to provide the Reliably host as a secret or via the Reliably's "
        "configuration's file."
    )


def test_missing_org_from_secrets() -> None:
    with pytest.raises(ActivityFailed) as ex:
        get_auth_info(
            {
                "reliably_config_path": "",
            },
            {"token": "78890", "host": "reliably.dev"},
        )
    assert str(ex.value) == (
        "Make sure to provide the current Reliably org as a secret or via the"
        " Reliably's configuration's file."
    )


def test_no_config_at_path_and_no_secrets_provided() -> None:
    with pytest.raises(ActivityFailed) as ex:
        get_auth_info({"reliably_config_path": str(uuid.uuid4())}, None)
    assert str(ex.value) == (
        "Make sure to login against Reliably's services and/or provide the correct"
        " authentication information to the experiment."
    )
