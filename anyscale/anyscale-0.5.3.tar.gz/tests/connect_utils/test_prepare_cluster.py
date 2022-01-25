from typing import Any, Dict, List, Optional
from unittest.mock import ANY, call, Mock, patch

import pytest

from anyscale.connect_utils.prepare_cluster import PrepareClusterBlock
from anyscale.sdk.anyscale_client import (
    CreateCluster,
    StartClusterOptions,
    UpdateCluster,
)
from anyscale.sdk.anyscale_client.models import ListResponseMetadata
from anyscale.sdk.anyscale_client.models.cloud_list_response import CloudListResponse


@pytest.fixture
def mock_prepare_cluster_block():
    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster.PrepareClusterBlock",
        __init__=Mock(return_value=None),
    ):
        prepare_cluster_block = PrepareClusterBlock()
        prepare_cluster_block.anyscale_api_client = Mock()
        prepare_cluster_block.api_client = Mock()
        prepare_cluster_block._ray = Mock()
        prepare_cluster_block.log = Mock()
        prepare_cluster_block.block_label = ""
        return prepare_cluster_block


@pytest.mark.parametrize("cluster_name", [None, "test_cluster_name"])
@pytest.mark.parametrize("ray_cli_is_connected", [True, False])
def test_create_cluster(
    mock_prepare_cluster_block, cluster_name: Optional[str], ray_cli_is_connected: bool
):
    mock_prepare_cluster_block.anyscale_api_client.list_sessions = Mock(
        return_value=Mock(results=[], metadata=Mock(next_paging_token=None))
    )
    mock_prepare_cluster_block._ray.util.client.ray.is_connected = Mock(
        return_value=ray_cli_is_connected
    )
    mock_prepare_cluster_block._start_cluster = Mock()

    mock_prepare_cluster_block._create_cluster(
        "test_project_id",
        "test_build_id",
        "test_compute_template_id",
        cluster_name,
        100,
        None,
    )

    if not cluster_name:
        mock_prepare_cluster_block.anyscale_api_client.list_sessions.assert_called_once_with(
            "test_project_id", count=50, paging_token=None
        )
    if ray_cli_is_connected:
        mock_prepare_cluster_block._ray.util.disconnect.assert_called_once_with()
    mock_prepare_cluster_block._start_cluster.assert_called_once_with(
        project_id="test_project_id",
        cluster_name=cluster_name if cluster_name else "cluster-0",
        build_id="test_build_id",
        compute_template_id="test_compute_template_id",
        autosuspend_timeout=100,
        allow_public_internet_traffic=None,
    )


@pytest.mark.parametrize("start_required", [True, False])
@pytest.mark.parametrize("allow_public_internet_traffic", [True, False])
def test_start_cluster(
    mock_prepare_cluster_block,
    start_required: bool,
    allow_public_internet_traffic: bool,
):
    mock_cluster = Mock(id="test_cluster_id")
    mock_prepare_cluster_block._create_or_update_session_data = Mock(
        return_value=(mock_cluster, start_required)
    )
    mock_prepare_cluster_block._log_cluster_configs = Mock()
    mock_wait_for_session_start = Mock()
    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster",
        wait_for_session_start=mock_wait_for_session_start,
    ):
        mock_prepare_cluster_block._start_cluster(
            "test_cluster_name",
            "test_project_id",
            "test_build_id",
            "test_compute_template_id",
            100,
            allow_public_internet_traffic,
        )
    mock_prepare_cluster_block._create_or_update_session_data.assert_called_once_with(
        "test_project_id",
        "test_cluster_name",
        "test_build_id",
        "test_compute_template_id",
        100,
        bool(allow_public_internet_traffic),
    )
    mock_prepare_cluster_block._log_cluster_configs.assert_called_once_with(
        mock_cluster, "test_build_id", "test_compute_template_id", ANY
    )
    if start_required:
        mock_prepare_cluster_block.anyscale_api_client.start_cluster.assert_called_once_with(
            mock_cluster.id,
            StartClusterOptions(
                cluster_environment_build_id="test_build_id",
                cluster_compute_id="test_compute_template_id",
                allow_public_internet_traffic=allow_public_internet_traffic,
            ),
        )
        mock_wait_for_session_start.assert_called_once_with(
            "test_cluster_name",
            "test_project_id",
            mock_prepare_cluster_block.api_client,
            log=mock_prepare_cluster_block.log,
            block_label=mock_prepare_cluster_block.block_label,
        )


@pytest.mark.parametrize("cluster_exists", [True, False])
@pytest.mark.parametrize("start_required", [True, False])
@pytest.mark.parametrize("idle_timeout", [None, 100])
def test_create_or_update_session_data(
    mock_prepare_cluster_block,
    cluster_exists: bool,
    start_required: bool,
    idle_timeout: Optional[int],
):
    mock_cluster = Mock(state="Running", id="test_cluster_id")
    mock_get_cluster = Mock(return_value=(mock_cluster if cluster_exists else None))
    mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster = Mock(
        return_value=start_required
    )

    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster", get_cluster=mock_get_cluster
    ):
        mock_prepare_cluster_block._create_or_update_session_data(
            "test_cluster_name",
            "test_project_id",
            "test_build_id",
            "test_compute_template_id",
            idle_timeout,
            None,
        )

    mock_get_cluster.assert_called_once_with(
        mock_prepare_cluster_block.anyscale_api_client,
        "test_project_id",
        "test_cluster_name",
    )

    if not cluster_exists:
        mock_prepare_cluster_block.anyscale_api_client.create_cluster.assert_called_once_with(
            CreateCluster(
                name="test_cluster_name",
                project_id="test_project_id",
                cluster_environment_build_id="test_build_id",
                cluster_compute_id="test_compute_template_id",
                idle_timeout_minutes=idle_timeout,
                allow_public_internet_traffic=None,
            )
        )
        mock_prepare_cluster_block.anyscale_api_client.update_cluster.assert_not_called()
        mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster.assert_not_called()
    else:
        mock_prepare_cluster_block.anyscale_api_client.create_cluster.assert_not_called()
        mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster.assert_called_once_with(
            "test_project_id", mock_cluster, print_warnings=False
        )
        if idle_timeout:
            mock_prepare_cluster_block.anyscale_api_client.update_cluster.assert_called_once_with(
                mock_cluster.id, UpdateCluster(idle_timeout_minutes=idle_timeout)
            )


@pytest.mark.parametrize("needs_update", [True, False])
@pytest.mark.parametrize("cluster_exists", [True, False])
@pytest.mark.parametrize("cluster_name", ["test_cluster_name", None])
@pytest.mark.parametrize("cluster_state", ["Running", "Other"])
def test_check_if_cluster_needs_start(
    mock_prepare_cluster_block,
    needs_update: bool,
    cluster_exists: bool,
    cluster_name: Optional[str],
    cluster_state: str,
):
    mock_cluster = Mock(state=cluster_state)
    mock_cluster.name = cluster_name
    mock_prepare_cluster_block.anyscale_api_client.search_sessions = Mock(
        return_value=Mock(results=[mock_cluster] if cluster_exists else [])
    )

    if not cluster_name or cluster_state != "Running" or not cluster_exists:
        assert mock_prepare_cluster_block._check_if_cluster_needs_start(
            "test_project_id", cluster_name, needs_update
        )
    else:
        assert (
            mock_prepare_cluster_block._check_if_cluster_needs_start(
                "test_project_id", cluster_name, needs_update
            )
            == needs_update
        )

    if cluster_name:
        mock_prepare_cluster_block.anyscale_api_client.search_sessions.assert_called_once_with(
            "test_project_id", {"name": {"equals": cluster_name}}
        )


@pytest.mark.parametrize("cluster_env_name", ["test_cluster_env_name", None])
def test_get_cluster_build(mock_prepare_cluster_block, cluster_env_name: Optional[str]):
    mock_build = Mock()
    mock_prepare_cluster_block._get_cluster_env_build = Mock(return_value=mock_build)
    mock_prepare_cluster_block._get_default_cluster_env_build = Mock(
        return_value=mock_build
    )

    assert (
        mock_prepare_cluster_block._get_cluster_build(cluster_env_name, None)
        == mock_build
    )

    if cluster_env_name:
        mock_prepare_cluster_block._get_cluster_env_build.assert_called_once_with(
            cluster_env_name, None
        )
    else:
        mock_prepare_cluster_block._get_default_cluster_env_build.assert_called_once_with()


@pytest.mark.parametrize("clust_env_revision", [None, 1])
def test_get_cluster_env_build(
    mock_prepare_cluster_block, clust_env_revision: Optional[int]
):
    mock_cluster_env = Mock(id="test_app_template_id")
    mock_cluster_env.name = "test_cluster_env_name"
    mock_prepare_cluster_block.anyscale_api_client.list_app_configs = Mock(
        return_value=Mock(
            results=[mock_cluster_env], metadata=Mock(next_paging_token=None)
        )
    )
    mock_build1 = Mock(id="build1", revision=1)
    mock_build2 = Mock(id="build2", revision=2)
    mock_prepare_cluster_block.anyscale_api_client.list_builds = Mock(
        return_value=Mock(
            results=[mock_build1, mock_build2], metadata=Mock(next_paging_token=None)
        )
    )

    if clust_env_revision == 1:
        assert (
            mock_prepare_cluster_block._get_cluster_env_build(
                "test_cluster_env_name", clust_env_revision
            )
            == mock_build1
        )
    else:
        assert (
            mock_prepare_cluster_block._get_cluster_env_build(
                "test_cluster_env_name", clust_env_revision
            )
            == mock_build2
        )


@pytest.mark.parametrize("build_pr", [None, "test_build_pr"])
@pytest.mark.parametrize("build_commit", [None, "test_build_commit"])
@pytest.mark.parametrize("cluster_env_name", [None, "test_cluster_env:name"])
@pytest.mark.parametrize("cluster_env_dict", [None, {"key": "val"}])
def test_build_cluster_env_if_needed(
    mock_prepare_cluster_block,
    build_pr: Optional[str],
    build_commit: Optional[str],
    cluster_env_name: Optional[str],
    cluster_env_dict: Optional[Dict[str, Any]],
):
    mock_prepare_cluster_block._build_app_config_from_source = Mock(
        return_value="test_built_cluster_env_name"
    )

    observed_result = mock_prepare_cluster_block._build_cluster_env_if_needed(
        "test_project_id",
        build_pr,
        build_commit,
        cluster_env_dict,
        cluster_env_name,
        False,
    )
    if build_pr or build_commit:
        assert observed_result == "test_built_cluster_env_name"
    elif cluster_env_dict:
        if cluster_env_name:
            assert observed_result == "test_cluster_env-name"
        else:
            assert observed_result.startswith("anonymous_cluster_env-")
        mock_prepare_cluster_block.anyscale_api_client.create_app_config.assert_called_once_with(
            {
                "name": observed_result,
                "project_id": "test_project_id",
                "config_json": cluster_env_dict,
            }
        )
    else:
        assert observed_result == cluster_env_name


@pytest.mark.parametrize("cluster_compute_name", [None, "test_cluster_compute_name"])
@pytest.mark.parametrize("cluster_compute_dict", [None, {"cloud_id": "mock_cloud_id"}])
@pytest.mark.parametrize("cloud_name", [None, "test_cloud_name"])
def test_get_cluster_compute_id(
    mock_prepare_cluster_block,
    cluster_compute_name: Optional[str],
    cluster_compute_dict: Optional[Dict[str, str]],
    cloud_name: Optional[str],
):
    mock_prepare_cluster_block._get_cloud_id = Mock(return_value="test_cloud_id")
    mock_default_config_obj = Mock()
    mock_config_obj_from_cluster_compute_dict = Mock()
    mock_prepare_cluster_block.anyscale_api_client.get_default_compute_config = Mock(
        return_value=Mock(result=mock_default_config_obj)
    )
    mock_prepare_cluster_block._register_compute_template = Mock(
        return_value="mock_registered_template"
    )
    mock_prepare_cluster_block._get_cluster_compute_id_from_name = Mock(
        return_value="mock_cluster_compute_template"
    )

    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster",
        ComputeTemplateConfig=Mock(
            return_value=mock_config_obj_from_cluster_compute_dict
        ),
    ):
        observed_result = mock_prepare_cluster_block._get_cluster_compute_id(
            "test_project_id", cluster_compute_name, cluster_compute_dict, cloud_name
        )

    if cluster_compute_name:
        mock_prepare_cluster_block._get_cluster_compute_id_from_name.assert_called_once_with(
            "test_project_id", cluster_compute_name
        )
        assert observed_result == "mock_cluster_compute_template"
    else:
        if cluster_compute_dict:
            mock_config_obj = mock_config_obj_from_cluster_compute_dict
        else:
            mock_prepare_cluster_block._get_cloud_id.assert_called_once_with(
                "test_project_id", cloud_name
            )
            mock_prepare_cluster_block.anyscale_api_client.get_default_compute_config.assert_called_once_with(
                "test_cloud_id"
            )
            mock_config_obj = mock_default_config_obj
        mock_prepare_cluster_block._register_compute_template.assert_called_once_with(
            "test_project_id", mock_config_obj
        )
        assert observed_result == "mock_registered_template"


@pytest.mark.parametrize("cluster_computes", [[], [Mock(id="test_cluster_compute_id")]])
def test_get_cluster_compute_id_from_name(
    mock_prepare_cluster_block, cluster_computes: List[Any]
):
    mock_prepare_cluster_block.api_client.search_compute_templates_api_v2_compute_templates_search_post = Mock(
        return_value=Mock(results=cluster_computes)
    )
    if len(cluster_computes) == 0:
        with pytest.raises(ValueError):
            mock_prepare_cluster_block._get_cluster_compute_id_from_name(
                "test_project_id", "test_cluster_compute_name"
            )
    else:
        assert (
            mock_prepare_cluster_block._get_cluster_compute_id_from_name(
                "test_project_id", "test_cluster_compute_name"
            )
            == cluster_computes[0].id
        )


def test_is_equal_cluster_compute(mock_prepare_cluster_block):
    def mock_get_compute_template(cluster_compute_id: str):
        if cluster_compute_id == "cluster_compute_1_id":
            return Mock(result=Mock(config=cluster_compute_1))
        elif cluster_compute_id == "cluster_compute_2_id":
            return Mock(result=Mock(config=cluster_compute_2))

    mock_prepare_cluster_block.anyscale_api_client.get_compute_template = Mock(
        side_effect=mock_get_compute_template
    )

    # Test cluster computes are equal
    cluster_compute_1 = "test_cluster_compute"
    cluster_compute_2 = "test_cluster_compute"
    assert mock_prepare_cluster_block._is_equal_cluster_compute(
        "cluster_compute_1_id", "cluster_compute_2_id"
    )

    # Test cluster_computes are different
    cluster_compute_1 = "test_cluster_compute"
    cluster_compute_2 = "test_diff_cluster_compute"
    assert not mock_prepare_cluster_block._is_equal_cluster_compute(
        "cluster_compute_1_id", "cluster_compute_2_id"
    )


@pytest.mark.parametrize("cloud_name", [None, "test_cloud_name"])
@pytest.mark.parametrize("default_cloud_exists", [True, False])
def test_get_cloud_id(
    mock_prepare_cluster_block, cloud_name: Optional[str], default_cloud_exists: bool
):
    mock_prepare_cluster_block._get_organization_default_cloud = Mock(
        return_value="default_cloud_name" if default_cloud_exists else None
    )
    mock_prepare_cluster_block._get_last_used_cloud = Mock(
        return_value="last_used_cloud_name"
    )
    mock_get_cloud_id_and_name = Mock(return_value=("mock_cloud_id", Mock()))

    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster",
        get_cloud_id_and_name=mock_get_cloud_id_and_name,
    ):
        assert (
            mock_prepare_cluster_block._get_cloud_id("test_project_id", cloud_name)
            == "mock_cloud_id"
        )

    if cloud_name:
        mock_get_cloud_id_and_name.assert_called_once_with(
            mock_prepare_cluster_block.api_client, cloud_name=cloud_name
        )
    elif default_cloud_exists:
        mock_prepare_cluster_block._get_organization_default_cloud.assert_called_once_with()
        mock_get_cloud_id_and_name.assert_called_once_with(
            mock_prepare_cluster_block.api_client, cloud_name="default_cloud_name"
        )
    else:
        mock_prepare_cluster_block._get_organization_default_cloud.assert_called_once_with()
        mock_prepare_cluster_block._get_last_used_cloud.assert_called_once_with(
            "test_project_id"
        )
        mock_get_cloud_id_and_name.assert_called_once_with(
            mock_prepare_cluster_block.api_client, cloud_name="last_used_cloud_name"
        )


@pytest.mark.parametrize("default_cloud_exists", [True, False])
@pytest.mark.parametrize("default_cloud_permissions_exist", [True, False])
def test_get_organization_default_cloud(
    mock_prepare_cluster_block,
    default_cloud_exists: bool,
    default_cloud_permissions_exist: bool,
):
    mock_user = Mock(
        organizations=[
            Mock(
                default_cloud_id="test_default_cloud_id"
                if default_cloud_exists
                else None
            )
        ]
    )
    mock_prepare_cluster_block.api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=mock_user)
    )
    if not default_cloud_permissions_exist:
        mock_get_cloud_id_and_name = Mock(side_effect=Exception)
    else:
        mock_get_cloud_id_and_name = Mock(
            return_value=("test_default_cloud_id", "test_default_cloud_name")
        )

    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster",
        get_cloud_id_and_name=mock_get_cloud_id_and_name,
    ):
        if not default_cloud_exists or not default_cloud_permissions_exist:
            assert mock_prepare_cluster_block._get_organization_default_cloud() is None
        else:
            assert (
                mock_prepare_cluster_block._get_organization_default_cloud()
                == "test_default_cloud_name"
            )
    mock_prepare_cluster_block.api_client.get_user_info_api_v2_userinfo_get.assert_called_once_with()
    if default_cloud_exists:
        mock_get_cloud_id_and_name.assert_called_once_with(
            mock_prepare_cluster_block.api_client, cloud_id="test_default_cloud_id"
        )


@pytest.mark.parametrize("cloud_id", ["test_cloud_id", None])
def test_get_last_used_cloud(mock_prepare_cluster_block, cloud_id: Optional[str]):
    mock_prepare_cluster_block.anyscale_api_client.get_project = Mock(
        return_value=Mock(result=Mock(last_used_cloud_id=cloud_id))
    )
    mock_cloud = Mock(id="test_cloud_id")
    mock_cloud.name = "test_cloud_name"
    mock_prepare_cluster_block.anyscale_api_client.get_cloud = Mock(
        return_value=Mock(result=mock_cloud)
    )
    mock_prepare_cluster_block._get_all_clouds = Mock(return_value=[mock_cloud])

    assert (
        mock_prepare_cluster_block._get_last_used_cloud("test_project_id")
        == "test_cloud_name"
    )
    mock_prepare_cluster_block.anyscale_api_client.get_project.assert_called_once_with(
        "test_project_id"
    )
    if cloud_id:
        mock_prepare_cluster_block.anyscale_api_client.get_cloud.assert_called_once_with(
            "test_cloud_id"
        )
    else:
        mock_prepare_cluster_block._get_all_clouds.assert_called_once_with()


@pytest.mark.parametrize("build_matches", [True, False])
@pytest.mark.parametrize("cluster_compute_matches", [True, False])
@pytest.mark.parametrize("allow_public_internet_traffic_matches", [True, False])
def test_validate_new_cluster_compute_and_env_match_existing_cluster(
    mock_prepare_cluster_block,
    build_matches: bool,
    cluster_compute_matches: bool,
    allow_public_internet_traffic_matches: bool,
):
    mock_cluster = Mock()
    mock_cluster.build_id = "mock_build_id1"
    mock_cluster.allow_public_internet_traffic = True
    mock_prepare_cluster_block.cluster_env_name = "test_cluster_env_name"
    mock_prepare_cluster_block.cluster_env_revision = "test_cluster_env_revision"
    mock_prepare_cluster_block.cluster_compute_name = "test_cluster_compute_name"
    mock_prepare_cluster_block.cluster_compute_dict = "test_cluster_compute_dict"
    mock_prepare_cluster_block.cloud_name = "test_cloud_name"
    mock_prepare_cluster_block.cluster_env_dict = "test_cluster_env_dict"
    mock_prepare_cluster_block._get_cluster_compute_id = Mock()

    if build_matches:
        mock_prepare_cluster_block._get_cluster_build = Mock(
            return_value=Mock(id="mock_build_id1")
        )
    else:
        mock_prepare_cluster_block._get_cluster_build = Mock(
            return_value=Mock(id="mock_build_id2")
        )

    mock_prepare_cluster_block._is_equal_cluster_compute = Mock(
        return_value=cluster_compute_matches
    )

    mock_prepare_cluster_block.allow_public_internet_traffic = (
        allow_public_internet_traffic_matches
    )

    observed_result = mock_prepare_cluster_block._validate_new_cluster_compute_and_env_match_existing_cluster(
        "test_projet_id", mock_cluster,
    )
    if (
        not build_matches
        or not not cluster_compute_matches
        or not allow_public_internet_traffic_matches
    ):
        assert observed_result


def test_get_all_clouds(mock_prepare_cluster_block) -> None:
    mock_cloud_1 = Mock()
    mock_cloud_1.name = "cloud_1"
    mock_cloud_2 = Mock()
    mock_cloud_2.name = "cloud_2"

    mock_prepare_cluster_block.anyscale_api_client.search_clouds.side_effect = [
        CloudListResponse(
            results=[mock_cloud_1],
            metadata=ListResponseMetadata(
                total=2, next_paging_token="next_paging_token"
            ),
        ),
        CloudListResponse(
            results=[mock_cloud_2], metadata=ListResponseMetadata(total=2),
        ),
    ]

    all_clouds = mock_prepare_cluster_block._get_all_clouds()
    assert all_clouds == [mock_cloud_1, mock_cloud_2]
    mock_prepare_cluster_block.anyscale_api_client.search_clouds.assert_has_calls(
        [
            call({"paging": {"count": 50}}),
            call({"paging": {"count": 50, "paging_token": "next_paging_token"}}),
        ]
    )


@pytest.mark.parametrize("cluster_needs_start", [True, False])
@pytest.mark.parametrize("cluster_name", ["test_cluster_name", None])
@pytest.mark.parametrize("cluster_compute_name", ["test_cluster_compute_name", None])
@pytest.mark.parametrize("cluster_env_name", ["test_cluster_env_name", None])
def test_init(
    cluster_needs_start: bool,
    cluster_name: Optional[str],
    cluster_compute_name: Optional[str],
    cluster_env_name: Optional[str],
):
    if not cluster_needs_start and not cluster_name:
        return

    mock_check_if_cluster_needs_start = Mock(return_value=cluster_needs_start)
    mock_cluster = Mock(
        cloud_id="mock_cloud_id", compute_template_id="mock_cluster_compute_id"
    )
    mock_cluster.name = "test_cluster_name"
    mock_build_cluster_env_if_needed = Mock(return_value=cluster_env_name)
    mock_get_cluster_build = Mock(return_value=Mock(id="mock_build_id"))
    mock_get_cloud_id = Mock(return_value="mock_cloud_id")
    mock_get_cluster_compute_id = Mock(return_value="mock_cluster_compute_id")
    mock_wait_for_app_build = Mock()
    mock_create_cluster = Mock(return_value="test_cluster_name")
    mock_validate_new_cluster_compute_and_env_match_existing_cluster = Mock()
    mock_log_cluster_configs = Mock()
    mock_cluster_compute_dict = Mock()
    mock_force_rebuild = Mock()
    mock_cluster_env_dict = Mock()
    mock_cluster_env_revision = Mock()

    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster.PrepareClusterBlock",
        _log_cluster_configs=mock_log_cluster_configs,
        _validate_new_cluster_compute_and_env_match_existing_cluster=mock_validate_new_cluster_compute_and_env_match_existing_cluster,
        _create_cluster=mock_create_cluster,
        _wait_for_app_build=mock_wait_for_app_build,
        _get_cluster_compute_id=mock_get_cluster_compute_id,
        _get_cloud_id=mock_get_cloud_id,
        _get_cluster_build=mock_get_cluster_build,
        _build_cluster_env_if_needed=mock_build_cluster_env_if_needed,
        _check_if_cluster_needs_start=mock_check_if_cluster_needs_start,
    ), patch.multiple(
        "anyscale.connect_utils.prepare_cluster",
        get_cluster=Mock(return_value=mock_cluster),
        get_auth_api_client=Mock(return_value=Mock()),
    ):
        prepare_cluster_block = PrepareClusterBlock(
            project_id="test_project_id",
            cluster_name=cluster_name,
            autosuspend_timeout=10,
            allow_public_internet_traffic=None,
            needs_update=False,
            cluster_compute_name=cluster_compute_name,
            cluster_compute_dict=mock_cluster_compute_dict,
            cloud_name="test_cloud_name",
            build_pr=None,
            force_rebuild=mock_force_rebuild,
            build_commit=None,
            cluster_env_name=cluster_env_name,
            cluster_env_dict=mock_cluster_env_dict,
            cluster_env_revision=mock_cluster_env_revision,
            ray=Mock(),
        )
        assert prepare_cluster_block.cluster_name == "test_cluster_name"

    mock_check_if_cluster_needs_start.assert_called_once_with(
        "test_project_id", cluster_name, False
    )
    if cluster_needs_start:
        mock_build_cluster_env_if_needed.assert_called_once_with(
            "test_project_id",
            None,
            None,
            mock_cluster_env_dict,
            cluster_env_name,
            mock_force_rebuild,
        )
        if cluster_env_name or not cluster_name:
            mock_get_cluster_build.assert_called_once_with(
                cluster_env_name, mock_cluster_env_revision
            )
            build_id = "mock_build_id"
        else:
            build_id = mock_cluster.build_id

        mock_get_cloud_id.assert_called_once_with("test_project_id", "test_cloud_name")
        if cluster_compute_name:
            mock_get_cluster_compute_id.assert_called_once_with(
                "test_project_id",
                cluster_compute_name,
                mock_cluster_compute_dict,
                "test_cloud_name",
            )
        mock_wait_for_app_build.assert_called_once_with("test_project_id", build_id)
        mock_create_cluster.assert_called_once_with(
            project_id="test_project_id",
            build_id=build_id,
            compute_template_id="mock_cluster_compute_id",
            cluster_name=cluster_name,
            autosuspend_timeout=10,
            allow_public_internet_traffic=None,
        )
    else:
        mock_validate_new_cluster_compute_and_env_match_existing_cluster.assert_called_once_with(
            project_id="test_project_id", running_cluster=mock_cluster
        )
        mock_log_cluster_configs.assert_called_once_with(
            mock_cluster, mock_cluster.build_id, mock_cluster.compute_template_id, ANY
        )
        mock_create_cluster.assert_not_called()
