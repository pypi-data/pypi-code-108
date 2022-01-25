import os
import tempfile
from typing import Any, Dict, Generator
from unittest.mock import Mock, patch

import pytest
import yaml

from anyscale.client.openapi_client.models import (
    AutoscalerCredentials,
    AutoscalercredentialsResponse,
    SessionDetails,
    SessiondetailsResponse,
    SessionSshKey,
    SessionsshkeyResponse,
)
from anyscale.cluster_config import (
    _configure_autoscaler_credentials,
    _configure_cluster_name,
    _configure_ssh_key,
    _update_file_mounts,
)
from anyscale.shared_anyscale_utils.project import CLUSTER_YAML_TEMPLATE


def test_configure_cluster_name(base_mock_api_client: Mock) -> None:
    initial_config: Dict[str, Any] = {}
    initial_config_copy = initial_config.copy()
    cluster_name = "CLUSTER_NAME_EXAMPLE"
    base_mock_api_client.get_session_details_api_v2_sessions_session_id_details_get = Mock(
        return_value=SessiondetailsResponse(
            result=SessionDetails(id="session_id", cluster_name=cluster_name)
        )
    )
    new_config = _configure_cluster_name(
        initial_config, "session_id", base_mock_api_client
    )

    assert initial_config == initial_config_copy
    assert new_config.get("cluster_name") == cluster_name


def test_configure_ssh_key(base_mock_api_client: Mock) -> None:
    base_mock_api_client.get_session_ssh_key_api_v2_sessions_session_id_ssh_key_get = Mock(
        return_value=SessionsshkeyResponse(
            result=SessionSshKey(key_name="SSH_KEY", private_key="PRIVATE_KEY")
        )
    )
    input_config = yaml.safe_load(CLUSTER_YAML_TEMPLATE)
    input_config["head_node"] = {}
    input_config["worker_nodes"] = {}
    with tempfile.TemporaryDirectory() as directory:
        output_config = _configure_ssh_key(
            input_config, "session_id", base_mock_api_client, directory
        )
        with open(os.path.join(directory, "SSH_KEY.pem"), "r") as f:
            assert f.read() == "PRIVATE_KEY"
    assert "SSH_KEY" in output_config["auth"]["ssh_private_key"]


def test_configure_autoscaler_credentials(base_mock_api_client: Mock) -> None:
    base_mock_api_client.get_session_autoscaler_credentials_api_v2_sessions_session_id_autoscaler_credentials_get = Mock(
        return_value=AutoscalercredentialsResponse(
            result=AutoscalerCredentials(credentials="cred")
        )
    )
    output_config = _configure_autoscaler_credentials(
        yaml.safe_load(CLUSTER_YAML_TEMPLATE), "session_id", base_mock_api_client
    )
    assert output_config["provider"]["aws_credentials"] == "cred"


@pytest.fixture()
def config_patches() -> Generator[str, None, None]:
    remote_project_directory_name = "remote_proj_directory"
    with patch.multiple(
        "anyscale.cluster_config", get_project_id=Mock(return_value="project_id")
    ), patch.multiple(
        "anyscale.util",
        get_project_directory_name=Mock(return_value=remote_project_directory_name),
    ):
        yield remote_project_directory_name


def test_update_file_mounts(config_patches: str) -> None:
    project_root_dir = "/home/fake/root/dir"
    new_config = _update_file_mounts({}, project_root_dir)
    assert new_config["file_mounts"] == {
        f"/home/ray/{config_patches}": project_root_dir
    }


def test_update_file_mounts_with_working_dir(config_patches: str) -> None:
    project_root_dir = "/home/fake/root/dir"
    input_config: Dict[str, Any] = {}
    working_dir = "/home/fake/working_dir/dir"
    input_config.setdefault("metadata", {}).setdefault("anyscale", {})[
        "working_dir"
    ] = working_dir
    new_config = _update_file_mounts(input_config, project_root_dir)
    assert new_config["file_mounts"] == {working_dir: project_root_dir}


def test_update_file_mounts_if_proj_dir_exists(config_patches: str) -> None:
    # Updates project directory sync in file mounts when there is already a file
    # mount in the cluster config that maps to the remote project directory location.
    project_usr1_root_dir = "/home/usr1/root/dir"
    project_usr2_root_dir = "/home/usr2/root/dir"
    remote_project_directory_name = f"/home/ray/{config_patches}"

    mock_path_exists = Mock(side_effect=lambda x: x == project_usr2_root_dir)
    mock_path_samefile = Mock(side_effect=lambda x, y: x == y)

    with patch.multiple(
        "os.path", exists=mock_path_exists, samefile=mock_path_samefile
    ):
        # Handles the case when the local directory in the project directory sync doesn't exist. This can
        # happen when getting the cluster config on a session that is shared, or if the local directory
        # no longer exists.
        input_config: Dict[str, Any] = {
            "file_mounts": {remote_project_directory_name: project_usr1_root_dir}
        }
        new_config = _update_file_mounts(input_config, project_usr2_root_dir)
        assert new_config["file_mounts"] == {
            remote_project_directory_name: project_usr2_root_dir
        }

        # Handles the case when the project directory sync is already correctlly updated. This happens for
        # subsequent commands on a session you created.
        input_config = {
            "file_mounts": {remote_project_directory_name: project_usr2_root_dir}
        }
        new_config = _update_file_mounts(input_config, project_usr2_root_dir)
        assert new_config["file_mounts"] == {
            remote_project_directory_name: project_usr2_root_dir
        }
