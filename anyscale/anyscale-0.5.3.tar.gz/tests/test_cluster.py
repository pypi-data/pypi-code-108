from unittest.mock import Mock, patch

import click
import pytest

from anyscale.cluster import get_job_submission_client_cluster_info


@pytest.mark.parametrize(
    "mock_sessions_return_value",
    [
        Mock(results=[]),
        Mock(
            results=[Mock(host_name="mock_host_name", access_token="mock_access_token")]
        ),
    ],
)
@pytest.mark.parametrize("create_cluster_if_needed", [True, False])
def test_get_job_submission_client_cluster_info(
    mock_sessions_return_value: Mock, create_cluster_if_needed: bool
):
    mock_project_definition = Mock()
    mock_project_definition.root = "/some/directory"
    mock_load_project_or_throw = Mock(return_value=mock_project_definition)

    mock_get_project_id = Mock(return_value="mock_project_id")
    mock_api_client = Mock()
    mock_api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=Mock(id="mock_user_id"))
    )
    mock_api_client.list_sessions_api_v2_sessions_get = Mock(
        return_value=mock_sessions_return_value
    )
    mock_project_block = Mock(return_value=Mock(project_id="mock_project_id"))
    mock_prepare_cluster_block = Mock(
        return_value=Mock(cluster_name="mock_cluster_name")
    )

    class MockClientBuilder:
        def __init__(self, **kwargs):
            self._project_dir = "_project_dir"
            self._project_name = "_project_name"
            self._cluster_name = "_cluster_name"
            self._autosuspend_timeout = ("_autosuspend_timeout",)
            self._allow_public_internet_traffic = "_allow_public_internet_traffic"
            self._needs_update = "_needs_update"
            self._cluster_compute_name = "_cluster_compute_name"
            self._cluster_compute_dict = "_cluster_compute_dict"
            self._cloud_name = "_cloud_name"
            self._build_pr = "_build_pr"
            self._force_rebuild = "_force_rebuild"
            self._build_commit = "_build_commit"
            self._cluster_env_name = "_cluster_env_name"
            self._cluster_env_dict = "_cluster_env_dict"
            self._cluster_env_revision = "_cluster_env_revision"
            self._ray = "_ray"

    mock_client_builder = MockClientBuilder()

    with patch.multiple(
        "anyscale.cluster",
        load_project_or_throw=mock_load_project_or_throw,
        get_project_id=mock_get_project_id,
        ClientBuilder=MockClientBuilder,
        create_prepare_cluster_block=mock_prepare_cluster_block,
        create_project_block=mock_project_block,
        get_auth_api_client=Mock(return_value=Mock(api_client=mock_api_client)),
    ):
        if len(mock_sessions_return_value.results) == 0:
            with pytest.raises(click.ClickException):
                get_job_submission_client_cluster_info(
                    "mock_cluster_name", create_cluster_if_needed
                )
        else:
            get_job_submission_client_cluster_info(
                "mock_cluster_name", create_cluster_if_needed
            )

    mock_api_client.list_sessions_api_v2_sessions_get.assert_called_once_with(
        project_id="mock_project_id", active_only=True, name="mock_cluster_name"
    )

    if create_cluster_if_needed:
        mock_project_block.assert_called_once_with(
            mock_client_builder._project_dir, mock_client_builder._project_name
        )
        mock_prepare_cluster_block.assert_called_once_with(
            project_id="mock_project_id",
            cluster_name=mock_client_builder._cluster_name,
            autosuspend_timeout=mock_client_builder._autosuspend_timeout,
            allow_public_internet_traffic=mock_client_builder._allow_public_internet_traffic,
            needs_update=mock_client_builder._needs_update,
            cluster_compute_name=mock_client_builder._cluster_compute_name,
            cluster_compute_dict=mock_client_builder._cluster_compute_dict,
            cloud_name=mock_client_builder._cloud_name,
            build_pr=mock_client_builder._build_pr,
            force_rebuild=mock_client_builder._force_rebuild,
            build_commit=mock_client_builder._build_commit,
            cluster_env_name=mock_client_builder._cluster_env_name,
            cluster_env_dict=mock_client_builder._cluster_env_dict,
            cluster_env_revision=mock_client_builder._cluster_env_revision,
            ray=mock_client_builder._ray,
        )
