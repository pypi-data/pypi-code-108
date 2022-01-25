from typing import Any, Dict, Optional
from unittest.mock import ANY, Mock, patch

import click
from click.exceptions import ClickException
import pytest
import yaml
from yaml.loader import SafeLoader

from anyscale.controllers.cluster_compute_controller import (
    ClusterComputeController,
    CreateClusterComputeConfigModel,
)
from anyscale.sdk.anyscale_client.models.cluster_compute import ClusterCompute
from anyscale.sdk.anyscale_client.models.cluster_computes_query import (
    ClusterComputesQuery,
)
from anyscale.sdk.anyscale_client.models.clustercompute_list_response import (
    ClustercomputeListResponse,
)
from anyscale.sdk.anyscale_client.models.clustercompute_response import (
    ClustercomputeResponse,
)
from anyscale.sdk.anyscale_client.models.create_cluster_compute import (
    CreateClusterCompute,
)
from anyscale.sdk.anyscale_client.models.text_query import TextQuery


@pytest.fixture()
def mock_auth_api_client(mock_api_client: Mock, mock_sdk_client: Mock):
    mock_auth_api_client = Mock(
        api_client=mock_api_client, anyscale_api_client=mock_sdk_client,
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=mock_auth_api_client),
    ):
        yield


@pytest.fixture()
def example_compute_config() -> Dict[str, Any]:

    example_compute_config_str = """

    {
    "cloud_id": "cld_HSrCZdMCYDe1NmMCJhYRgQ4p",
    "max_workers": 20,
    "allowed_azs": null,
    "head_node_type": {
        "name": "head-node-type",
        "instance_type": "m5.2xlarge",
        "resources": null
    },
    "worker_node_types": [
        {
        "name": "worker-node-type-0",
        "instance_type": "m5.4xlarge",
        "resources": null,
        "min_workers": null,
        "max_workers": 10,
        "use_spot": false
        },
        {
        "name": "worker-node-type-1",
        "instance_type": "g4dn.4xlarge",
        "resources": null,
        "min_workers": null,
        "max_workers": 10,
        "use_spot": false
        }
    ],
    "aws": null,
    "gcp": null,
    "azure": null
    }
    """
    return yaml.load(example_compute_config_str, Loader=SafeLoader)


@pytest.fixture()
def mock_api_client() -> Mock:
    mock_api_client = Mock()

    return mock_api_client


@pytest.fixture()
def mock_sdk_client(cluster_compute_test_data: ClusterCompute) -> Mock:
    mock_sdk_client = Mock()

    mock_sdk_client.create_cluster_compute = Mock(
        return_value=ClustercomputeResponse(result=cluster_compute_test_data)
    )
    mock_sdk_client.delete_cluster_compute = Mock()
    mock_sdk_client.search_cluster_computes = Mock(
        return_value=ClustercomputeListResponse(results=[cluster_compute_test_data])
    )
    mock_sdk_client.get_cluster_compute = Mock()

    return mock_sdk_client


@pytest.mark.parametrize("cloud_id", [None, "test_cloud_id"])
@pytest.mark.parametrize("cloud", [None, "test_cloud_name"])
def test_create_validation(
    example_compute_config: Dict[str, Any],
    cloud_id: Optional[str],
    cloud: Optional[str],
):
    mock_get_cloud_id_and_name = Mock(return_value=("test_cloud_id", "test_cloud_name"))
    example_compute_config["cloud_id"] = cloud_id
    example_compute_config["cloud"] = cloud
    with patch.multiple(
        "anyscale.controllers.cluster_compute_controller",
        get_cloud_id_and_name=mock_get_cloud_id_and_name,
    ):
        if bool(cloud_id) + bool(cloud) != 1:
            with pytest.raises(click.ClickException):
                CreateClusterComputeConfigModel(**example_compute_config)
        else:
            CreateClusterComputeConfigModel(**example_compute_config)


@pytest.mark.parametrize("name", [None, "test_name"])
def test_create(
    mock_auth_api_client, name: Optional[str], example_compute_config: Dict[str, Any],
) -> None:
    cluster_compute_controller = ClusterComputeController()

    mock_load = Mock(return_value=example_compute_config)
    mock_cluster_compute_io = Mock()
    with patch.multiple("yaml", load=mock_load):
        cluster_compute_controller.create(mock_cluster_compute_io, name)

    example_compute_config["region"] = None
    cluster_compute_controller.anyscale_api_client.create_cluster_compute.assert_called_once_with(
        CreateClusterCompute(name=ANY, config=example_compute_config)
    )


@pytest.mark.parametrize("cluster_compute_name", [None, "test_name"])
@pytest.mark.parametrize("id", [None, "cpt_123"])
def test_delete(
    mock_auth_api_client,
    cluster_compute_name: Optional[str],
    id: Optional[str],
    cluster_compute_test_data: ClusterCompute,
) -> None:
    cluster_compute_controller = ClusterComputeController()

    if cluster_compute_name is None and id is None:
        with pytest.raises(ClickException):
            cluster_compute_controller.delete(cluster_compute_name, id)
        cluster_compute_controller.anyscale_api_client.delete_cluster_compute.assert_not_called()
    elif cluster_compute_name is not None and id is not None:
        with pytest.raises(ClickException):
            cluster_compute_controller.delete(cluster_compute_name, id)
        cluster_compute_controller.anyscale_api_client.delete_cluster_compute.assert_not_called()
    elif cluster_compute_name and id is None:
        cluster_compute_controller.delete(cluster_compute_name, id)
        cluster_compute_controller.anyscale_api_client.search_cluster_computes.assert_called_once_with(
            ClusterComputesQuery(name=TextQuery(equals=cluster_compute_name))
        )
        cluster_compute_controller.anyscale_api_client.delete_cluster_compute.assert_called_once_with(
            cluster_compute_test_data.id
        )
    elif cluster_compute_name is None and id:
        cluster_compute_controller.delete(cluster_compute_name, id)
        cluster_compute_controller.anyscale_api_client.get_cluster_compute.assert_called_once_with(
            id
        )
        cluster_compute_controller.anyscale_api_client.delete_cluster_compute.assert_called_once_with(
            id
        )


@pytest.mark.parametrize("cluster_compute_name", [None, "test_cluster_compute_name"])
@pytest.mark.parametrize("cluster_compute_id", [None, "test_cluster_compute_id"])
def test_get(
    mock_auth_api_client,
    cluster_compute_name: Optional[str],
    cluster_compute_id: Optional[str],
):
    cluster_compute_controller = ClusterComputeController()
    if (cluster_compute_name is None and cluster_compute_id is None) or (
        cluster_compute_name is not None and cluster_compute_id is not None
    ):
        with pytest.raises(click.ClickException):
            cluster_compute_controller.get(
                cluster_compute_name=cluster_compute_name,
                cluster_compute_id=cluster_compute_id,
            )
            return
    else:
        with patch.multiple(
            "anyscale.controllers.cluster_compute_controller",
            get_cluster_compute_from_name=Mock(
                return_value=Mock(id=cluster_compute_id)
            ),
        ):
            cluster_compute_controller.get(
                cluster_compute_name=cluster_compute_name,
                cluster_compute_id=cluster_compute_id,
            )
            cluster_compute_controller.api_client.get_compute_template_api_v2_compute_templates_template_id_get.assert_called_once_with(
                cluster_compute_id
            )


@pytest.mark.parametrize("cluster_compute_name", [None, "test_cluster_compute_name"])
@pytest.mark.parametrize("cluster_compute_id", [None, "test_cluster_compute_id"])
@pytest.mark.parametrize("include_shared", [True, False])
def test_list(
    mock_auth_api_client,
    cluster_compute_name: Optional[str],
    cluster_compute_id: Optional[str],
    include_shared: bool,
):
    cluster_compute_controller = ClusterComputeController()
    cluster_compute_controller.anyscale_api_client.search_cluster_computes = Mock(
        return_value=Mock(results=[Mock()], metadata=Mock(next_paging_token=None))
    )
    cluster_compute_controller.list(
        cluster_compute_name=cluster_compute_name,
        cluster_compute_id=cluster_compute_id,
        include_shared=include_shared,
        max_items=50,
    )

    if cluster_compute_id:
        cluster_compute_controller.anyscale_api_client.get_cluster_compute.assert_called_once_with(
            cluster_compute_id
        )
    elif cluster_compute_name:
        cluster_compute_controller.anyscale_api_client.search_cluster_computes.assert_called_once_with(
            {"name": {"equals": cluster_compute_name}, "paging": {"count": 1}}
        )
    else:
        if not include_shared:
            cluster_compute_controller.api_client.get_user_info_api_v2_userinfo_get.assert_called_once_with()
            cluster_compute_controller.anyscale_api_client.search_cluster_computes.assert_called_once_with(
                {"creator_id": ANY, "paging": {"count": 20}}
            )
