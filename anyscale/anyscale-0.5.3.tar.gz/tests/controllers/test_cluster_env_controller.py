from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from anyscale.controllers.cluster_env_controller import ClusterEnvController


def test_list_builds(mock_auth_api_client,):
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock",
        _validate_api_client_auth=Mock(),
        _validate_credentials_format=Mock(),
    ):
        cluster_env_controller = ClusterEnvController()
    mock_list_builds = Mock(
        return_value=[
            Mock(
                id="mock_build1",
                revision="mock_revision",
                status="mock_status",
                last_modified_at=datetime.now(),
            )
        ]
    )
    cluster_env_controller.anyscale_api_client.get_cluster_environment = Mock(
        return_value=Mock(result=Mock(name="mock_cluster_env_name"))
    )
    mock_get_cluster_env_from_name = Mock(return_value=Mock(id="mock_cluster_env_id"))

    with patch.multiple(
        "anyscale.controllers.cluster_env_controller",
        list_builds=mock_list_builds,
        get_cluster_env_from_name=mock_get_cluster_env_from_name,
    ):
        cluster_env_controller._list_builds("mock_cluster_env_name", None, max_items=20)
        mock_get_cluster_env_from_name.assert_called_with(
            "mock_cluster_env_name", cluster_env_controller.anyscale_api_client
        )
        mock_list_builds.assert_called_with(
            "mock_cluster_env_id",
            cluster_env_controller.anyscale_api_client,
            max_items=20,
        )

        cluster_env_controller._list_builds(None, "mock_cluster_env_id", max_items=20)
        mock_list_builds.assert_called_with(
            "mock_cluster_env_id",
            cluster_env_controller.anyscale_api_client,
            max_items=20,
        )
        cluster_env_controller.anyscale_api_client.get_cluster_environment.assert_called_with(
            "mock_cluster_env_id"
        )


@pytest.mark.parametrize("include_shared", [True, False])
def test_list_cluster_envs(
    mock_auth_api_client, include_shared: bool,
):
    cluster_env_controller = ClusterEnvController()
    mock_cluster_env = Mock()
    mock_cluster_env.name = "mock_cluster_env_name"
    cluster_env_controller.anyscale_api_client.search_cluster_environments = Mock(
        return_value=Mock(
            results=[mock_cluster_env], metadata=Mock(next_paging_token=None)
        )
    )
    cluster_env_controller.api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=Mock(id="mock_user_id"))
    )
    mock_get_build_from_cluster_env_identifier = Mock(
        return_value=Mock(id="mock_build_id")
    )
    cluster_env_controller.anyscale_api_client.get_cluster_environment_build = Mock(
        return_value=Mock(result=Mock(last_modified_at=datetime.now()))
    )

    with patch.multiple(
        "anyscale.controllers.cluster_env_controller",
        get_build_from_cluster_env_identifier=mock_get_build_from_cluster_env_identifier,
    ):
        cluster_env_controller._list_cluster_envs(include_shared, max_items=20)
        if not include_shared:
            cluster_env_controller.anyscale_api_client.search_cluster_environments.assert_called_with(
                {"creator_id": "mock_user_id", "paging": {"count": 20}}
            )
        else:
            cluster_env_controller.anyscale_api_client.search_cluster_environments.assert_called_with(
                {"creator_id": None, "paging": {"count": 20}}
            )
        mock_get_build_from_cluster_env_identifier.assert_called_with(
            "mock_cluster_env_name", cluster_env_controller.anyscale_api_client
        )
