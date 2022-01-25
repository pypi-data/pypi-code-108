from typing import Any, Dict, Mapping, Tuple
from unittest.mock import Mock, patch

import pytest

from anyscale.autoscaler.aws.node_provider import AnyscaleAWSNodeProvider
from anyscale.autoscaler.node_provider import AnyscaleInstanceManagerNodeProvider


@pytest.mark.parametrize(
    "node_provider_class_and_config",
    [
        (AnyscaleAWSNodeProvider, {"region": "us-west-2"}),
        (
            AnyscaleInstanceManagerNodeProvider,
            {
                "inner_provider": {
                    "region": "us-west-2",
                    "type": "aws",
                    "cli_token": "fake_token",
                    "host": "fake_host",
                    "cloud_id": "fake_cloud_id",
                }
            },
        ),
    ],
)
@pytest.mark.parametrize(
    "cluster_config",
    [
        pytest.param({"provider": {"aws_credentials": {}}}, id="has aws_credentials"),
        pytest.param(
            {"provider": {"inner_provider": {"aws_credentials": {}}}},
            id="has inner_provider",
        ),
    ],
)
def test_ensure_no_credentials_on_head_node_config(
    cluster_config: Mapping[str, Any],
    node_provider_class_and_config: Tuple[Any, Dict[str, Any]],
) -> None:
    node_provider_class, provider_config = node_provider_class_and_config
    with patch.multiple(
        "ray.autoscaler._private.aws.node_provider",
        make_ec2_client=Mock(return_value=None),
    ), patch.multiple(
        "anyscale.authenticate.AuthenticationBlock",
        _validate_api_client_auth=Mock(),
        _validate_credentials_format=Mock(),
    ):
        node_provider = node_provider_class(provider_config, "fake_cluster_name")

    cleaned_config = node_provider.prepare_for_head_node(cluster_config)

    provider_config = cleaned_config.get("provider", {})

    assert "aws_credentials" not in provider_config
    assert "aws_credentials" not in provider_config.get("inner_provider", {})


def test_create_node_return() -> None:
    mock_ec2_client = Mock()
    mock_instance_id = "fake_instance_id"
    mock_instance_ip = "fake_ip"
    mock_ec2_instance = Mock()
    mock_ec2_instance.id = mock_instance_id
    mock_ec2_instance.public_ip_address = mock_instance_ip
    mock_ec2_instance.state_reason = {}
    mock_ec2_instance.state = {"Name": "Fake Name"}
    mock_ec2_client.create_instances = Mock(return_value=[mock_ec2_instance])
    provider_config = {"region": "us-west-2", "cache_stopped_nodes": False}
    with patch.multiple(
        "ray.autoscaler._private.aws.node_provider",
        make_ec2_client=Mock(return_value=mock_ec2_client),
    ):
        node_provider = AnyscaleAWSNodeProvider(provider_config, "fake_cluster_name")
        created_node = node_provider.create_node({"SubnetIds": "123"}, tags={}, count=1)

        assert created_node[mock_instance_id]["PublicIpAddress"] == mock_instance_ip
