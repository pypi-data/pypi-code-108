import json
from typing import List
from unittest.mock import Mock, mock_open, patch

import click
import pytest

from anyscale.controllers.cluster_controller import ClusterController
from anyscale.sdk.anyscale_client import StartClusterOptions


@pytest.mark.parametrize(
    "cluster",
    [
        Mock(state="Running", cluster_environment_build_id="build1"),
        Mock(state="Terminated", cluster_environment_build_id="build1"),
    ],
)
@pytest.mark.parametrize(
    "build", [Mock(id="build1", revision=1), Mock(id="build2", revision=2)]
)
@pytest.mark.parametrize("cluster_compute", [Mock(id="compute1"), Mock(id="compute2")])
@pytest.mark.parametrize("passed_cluster_env", [True, False])
@pytest.mark.parametrize("passed_cluster_compute", [True, False])
def test_check_needs_start(
    cluster: Mock,
    build: Mock,
    cluster_compute: Mock,
    passed_cluster_env: bool,
    passed_cluster_compute: bool,
    mock_auth_api_client,
) -> None:
    cluster_controller = ClusterController()

    needs_start = cluster_controller._check_needs_start(
        cluster, build, cluster_compute, passed_cluster_env, passed_cluster_compute
    )
    if cluster.state != "Running":
        assert needs_start
    elif not passed_cluster_env and not passed_cluster_compute:
        assert not needs_start
    elif passed_cluster_env and cluster.cluster_environment_build_id != build.id:
        assert needs_start
    elif passed_cluster_compute and cluster.cluster_compute_id != cluster_compute.id:
        assert needs_start


def test_get_project_id_and_cluster_name_given_cluster_id(mock_auth_api_client):
    cluster_controller = ClusterController()

    # Test passing in cluster id only
    mock_cluster = Mock(id="mock_cluster_id", project_id="mock_project_id")
    mock_cluster.name = "mock_cluster_name"
    cluster_controller.anyscale_api_client.get_cluster = Mock(
        return_value=Mock(result=mock_cluster)
    )
    assert cluster_controller._get_project_id_and_cluster_name(
        cluster_id="mock_cluster_id",
        project_id=None,
        cluster_name=None,
        project_name=None,
    ) == ("mock_project_id", "mock_cluster_name")

    # Test passing in project id
    cluster_controller._get_or_generate_cluster_name = Mock(  # type: ignore
        return_value="mock_cluster_name1"
    )
    with patch.multiple(
        "anyscale.controllers.cluster_controller", validate_project_id=Mock(),
    ):
        assert cluster_controller._get_project_id_and_cluster_name(
            cluster_id=None,
            project_id="mock_project_id1",
            cluster_name=None,
            project_name=None,
        ) == ("mock_project_id1", "mock_cluster_name1")

    # Test passing in project name
    cluster_controller._get_or_generate_cluster_name = Mock(  # type: ignore
        return_value="mock_cluster_name1"
    )
    mock_get_proj_id_from_name = Mock(return_value="mock_project_id1")
    with patch.multiple(
        "anyscale.controllers.cluster_controller",
        validate_project_id=Mock(),
        get_proj_id_from_name=mock_get_proj_id_from_name,
    ):
        assert cluster_controller._get_project_id_and_cluster_name(
            cluster_id=None,
            project_id=None,
            cluster_name=None,
            project_name="mock_project_name1",
        ) == ("mock_project_id1", "mock_cluster_name1")

    # Test using default project
    cluster_controller._get_or_generate_cluster_name = Mock(  # type: ignore
        return_value="mock_cluster_name2"
    )
    cluster_controller.anyscale_api_client.get_default_project = Mock(
        return_value=Mock(result=Mock(id="mock_project_id2"))
    )
    with patch.multiple(
        "anyscale.controllers.cluster_controller",
        load_project_or_throw=Mock(side_effect=click.ClickException("")),
    ):
        assert cluster_controller._get_project_id_and_cluster_name(
            cluster_id=None, project_id=None, cluster_name=None, project_name=None
        ) == ("mock_project_id2", "mock_cluster_name2")


def test_get_cluster_env_and_build(mock_auth_api_client):
    cluster_controller = ClusterController()
    mock_get_build_from_cluster_env_identifier = Mock(return_value=Mock(id="build_id1"))
    mock_get_default_cluster_env_build = Mock(return_value=Mock(id="default_build_id"))

    with patch.multiple(
        "anyscale.controllers.cluster_controller",
        get_build_from_cluster_env_identifier=mock_get_build_from_cluster_env_identifier,
        get_default_cluster_env_build=mock_get_default_cluster_env_build,
    ):
        assert (
            cluster_controller._get_cluster_env_and_build(None)[1].id
            == "default_build_id"
        )
        assert (
            cluster_controller._get_cluster_env_and_build("mock_cluster_env")[1].id
            == "build_id1"
        )


def test_get_cluster_compute(mock_auth_api_client):
    cluster_controller = ClusterController()
    mock_get_cluster_compute_from_name = Mock(return_value=Mock(id="cluster_compute1"))
    cluster_controller.anyscale_api_client.create_cluster_compute = Mock(
        return_value=Mock(result=Mock(id="cluster_compute2"))
    )
    mock_get_default_cluster_compute = Mock(
        return_value=Mock(id="default_cluster_compute")
    )

    with patch(
        "builtins.open",
        mock_open(
            read_data=json.dumps(
                {
                    "cloud_id": "mock_cloud_id",
                    "region": "mock_region",
                    "head_node_type": "mock_head_node_type",
                    "worker_node_types": "mock_worker_node_types",
                }
            )
        ),
    ), patch.multiple(
        "anyscale.controllers.cluster_controller",
        get_cluster_compute_from_name=mock_get_cluster_compute_from_name,
        get_default_cluster_compute=mock_get_default_cluster_compute,
    ):
        assert (
            cluster_controller._get_cluster_compute(
                "cluster_compute_name1", None, None, "mock_project_id"
            ).id
            == "cluster_compute1"
        )
        assert (
            cluster_controller._get_cluster_compute(
                None, "cluster_compute_file2", None, "mock_project_id"
            ).id
            == "cluster_compute2"
        )
        assert (
            cluster_controller._get_cluster_compute(
                None, None, None, "mock_project_id"
            ).id
            == "default_cluster_compute"
        )


@pytest.mark.parametrize("needs_start", [True, False])
def test_start(mock_auth_api_client, needs_start: bool) -> None:
    cluster_controller = ClusterController()
    mock_build = Mock(id="build_id")
    mock_cluster_compute = Mock(id="cluster_compute_id")
    cluster_controller._get_project_id_and_cluster_name = Mock(  # type: ignore
        return_value=("mock_project_id", "mock_cluster_name")
    )
    cluster_controller._get_cluster_env_and_build = Mock(  # type: ignore
        return_value=(Mock(id="cluster_env_id"), mock_build)
    )
    cluster_controller._get_cluster_compute = Mock(return_value=mock_cluster_compute)  # type: ignore
    cluster_controller._create_or_update_cluster_data = Mock(  # type: ignore
        return_value=(Mock(id="cluster_id"), needs_start)
    )

    with patch.multiple(
        "anyscale.controllers.cluster_controller", wait_for_session_start=Mock(),
    ):
        cluster_controller.start(
            cluster_name=None,
            cluster_id="cluster_id",
            cluster_env_name="cluster_env_name",
            cluster_compute_name="cluster_compute_name",
            cluster_compute_file=None,
            cloud_name=None,
            idle_timeout=None,
            project_id=None,
            project_name=None,
        )

    cluster_controller._get_project_id_and_cluster_name.assert_called_once_with(
        "cluster_id", None, None, None
    )
    cluster_controller._get_cluster_env_and_build.assert_called_once_with(
        "cluster_env_name"
    )
    cluster_controller._get_cluster_compute.assert_called_once_with(
        "cluster_compute_name", None, None, "mock_project_id"
    )
    cluster_controller._create_or_update_cluster_data.assert_called_once_with(
        "mock_cluster_name",
        "mock_project_id",
        mock_build,
        mock_cluster_compute,
        True,
        True,
        None,
    )

    if needs_start:
        cluster_controller.anyscale_api_client.start_cluster.assert_called_once_with(
            "cluster_id",
            StartClusterOptions(
                cluster_environment_build_id=mock_build.id,
                cluster_compute_id=mock_cluster_compute.id,
            ),
        )


@pytest.mark.parametrize("cluster_list", [[], [Mock(id="mock_cluster_id")]])
def test_terminate(mock_auth_api_client, cluster_list: List[Mock],) -> None:
    cluster_controller = ClusterController()
    cluster_controller._get_project_id_and_cluster_name = Mock(  # type: ignore
        return_value=("mock_project_id", "mock_cluster_name")
    )
    cluster_controller.anyscale_api_client.search_clusters = Mock(  # type: ignore
        return_value=Mock(results=cluster_list)
    )

    with pytest.raises(click.ClickException):
        cluster_controller.terminate(None, None, None, None)
    with pytest.raises(click.ClickException):
        cluster_controller.terminate("cluster_name", "cluster_id", None, None)
    if len(cluster_list) == 0:
        with pytest.raises(click.ClickException):
            cluster_controller.terminate("cluster_name", None, "project_id", None)
    else:
        cluster_controller.terminate("cluster_name", None, "project_id", None)
        cluster_controller._get_project_id_and_cluster_name.assert_called_once_with(
            None, "project_id", "cluster_name", None
        )
        cluster_controller.anyscale_api_client.search_clusters.assert_called_once_with(
            {"project_id": "mock_project_id", "name": {"equals": "mock_cluster_name"}}
        )
        cluster_controller.anyscale_api_client.terminate_cluster.assert_called_once_with(
            "mock_cluster_id", {}
        )
