from unittest.mock import Mock, patch

from click import ClickException
import pytest

from anyscale.client.openapi_client.models.app_config_config_schema import (
    AppConfigConfigSchema,
)
from anyscale.client.openapi_client.models.baseimagesenum import BASEIMAGESENUM
from anyscale.controllers.config_controller import ConfigController
from anyscale.sdk.anyscale_client.models.cluster_compute_config import (
    ClusterComputeConfig,
)


def test_convert_compute_config_aws(mock_auth_api_client) -> None:
    config_controller = ConfigController()

    cluster_yaml = {
        "provider": {
            "type": "aws",
            "region": "us-west-2",
            "availability_zone": "us-west-2a,us-west-2b",
        },
        "max_workers": 10,
        "available_node_types": {
            "head-1": {"InstanceType": "m5.2xlarge"},
            "worker-node-0": {
                "InstanceType": "m5.4xlarge",
                "TagSpecifications": "fake",
            },
            "worker-node-1": {
                "InstanceType": "m5.8xlarge",
                "IamInstanceProfile": "fake2",
            },
        },
        "head_node_type": "head-1",
    }

    with patch.object(
        config_controller, "_convert_node_config_aws"
    ) as mock_convert_node_config_aws:

        def mock_convert_node_config(name, node_config, is_head_node=False):
            supported_option_keys = [
                "BlockDeviceMappings",
                "IamInstanceProfile",
                "TagSpecifications",
                "NetworkInterfaces",
            ]

            compute_config = {
                "name": name,
                "instance_type": node_config["InstanceType"],
            }

            if not is_head_node:
                compute_config["use_spot"] = False

            aws_options = {
                key: value
                for key, value in node_config.items()
                if key in supported_option_keys
            }

            return compute_config, aws_options

        mock_convert_node_config_aws.side_effect = mock_convert_node_config
        converted_compute_config = config_controller._convert_compute_config(
            "cld_1", cluster_yaml
        )

    assert (
        converted_compute_config.to_dict()
        == ClusterComputeConfig(
            cloud_id="cld_1",
            max_workers=10,
            region="us-west-2",
            allowed_azs=["us-west-2a", "us-west-2b"],
            head_node_type={
                "name": "head-1",
                "instance_type": "m5.2xlarge",
                "resources": None,
            },
            worker_node_types=[
                {
                    "name": "worker-node-0",
                    "instance_type": "m5.4xlarge",
                    "resources": None,
                    "min_workers": None,
                    "max_workers": None,
                    "use_spot": False,
                },
                {
                    "name": "worker-node-1",
                    "instance_type": "m5.8xlarge",
                    "resources": None,
                    "min_workers": None,
                    "max_workers": None,
                    "use_spot": False,
                },
            ],
            aws={"TagSpecifications": "fake", "IamInstanceProfile": "fake2"},
        ).to_dict()
    )


def test_convert_compute_config_legacy_config(mock_auth_api_client) -> None:
    config_controller = ConfigController()

    cluster_yaml = {
        "provider": {
            "type": "aws",
            "region": "us-west-2",
            "availability_zone": "us-west-2a,us-west-2b",
        },
        "max_workers": 10,
        "head_node": {"InstanceType": "m5.2xlarge"},
        "worker_nodes": [
            {"InstanceType": "m5.4xlarge", "TagSpecifications": "fake"},
            {"InstanceType": "m5.8xlarge", "IamInstanceProfile": "fake2"},
        ],
        "head_node_type": "head-1",
    }

    with pytest.raises(ClickException):
        config_controller._convert_compute_config("cld_1", cluster_yaml)


def test_convert_compute_config_gcp(mock_auth_api_client) -> None:
    config_controller = ConfigController()

    cluster_yaml = {
        "provider": {
            "type": "gcp",
            "region": "us-west-2",
            "availability_zone": "us-west-2a,us-west-2b",
        },
        "max_workers": 10,
        "available_node_types": {
            "head-1": {"InstanceType": "m5.2xlarge"},
            "worker-node-0": {
                "InstanceType": "m5.4xlarge",
                "TagSpecifications": "fake",
            },
            "worker-node-1": {
                "InstanceType": "m5.8xlarge",
                "IamInstanceProfile": "fake2",
            },
        },
        "head_node_type": "head-1",
    }

    with pytest.raises(ClickException):
        config_controller._convert_compute_config("cld_1", cluster_yaml)


def test_convert_node_config_aws(mock_auth_api_client) -> None:
    config_controller = ConfigController()

    head_node_type_config = {
        "node_config": {
            "InstanceType": "m5.8xlarge",
            "ImageId": "latest_dlami",
            "KeyName": "aguo-anyscale",
            "BlockDeviceMappings": [
                {"DeviceName": "/dev/sda1", "Ebs": {"VolumeSize": 300}}
            ],
            "TagSpecifications": [
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "anyscale-user", "Value": "aguo@anyscale.com"}],
                }
            ],
            "IamInstanceProfile": {"Arn": "arn:aws:iam:test1234"},
            "NetworkInterfaces": [
                {
                    "Groups": ["sg-1", "sg-2"],
                    "SubnetId": "subnet-1234",
                    "AssociatePublicIpAddress": True,
                }
            ],
        },
    }

    assert config_controller._convert_node_config_aws(
        "head-node", head_node_type_config, True
    ) == (
        {"name": "head-node", "instance_type": "m5.8xlarge"},
        {
            "BlockDeviceMappings": [
                {"DeviceName": "/dev/sda1", "Ebs": {"VolumeSize": 300}}
            ],
            "TagSpecifications": [
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "anyscale-user", "Value": "aguo@anyscale.com"}],
                }
            ],
            "IamInstanceProfile": {"Arn": "arn:aws:iam:test1234"},
            "NetworkInterfaces": [
                {
                    "Groups": ["sg-1", "sg-2"],
                    "SubnetId": "subnet-1234",
                    "AssociatePublicIpAddress": True,
                }
            ],
        },
    )

    worker_node_type_config = {
        "min_workers": 3,
        "max_workers": 3,
        "node_config": {
            "InstanceType": "m5.8xlarge",
            "ImageId": "latest_dlami",
            "KeyName": "aguo-anyscale",
            "BlockDeviceMappings": [
                {"DeviceName": "/dev/sda1", "Ebs": {"VolumeSize": 300}}
            ],
            "TagSpecifications": [
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "anyscale-user", "Value": "aguo@anyscale.com"}],
                }
            ],
            "IamInstanceProfile": {"Arn": "arn:aws:iam:test1234"},
            "NetworkInterfaces": [
                {
                    "Groups": ["sg-1", "sg-2"],
                    "SubnetId": "subnet-1234",
                    "AssociatePublicIpAddress": True,
                }
            ],
            "InstanceMarketOptions": {"MarketType": "spot"},
        },
    }

    assert config_controller._convert_node_config_aws(
        "worker-node-0", worker_node_type_config
    ) == (
        {
            "name": "worker-node-0",
            "instance_type": "m5.8xlarge",
            "min_workers": 3,
            "max_workers": 3,
            "use_spot": True,
        },
        {
            "BlockDeviceMappings": [
                {"DeviceName": "/dev/sda1", "Ebs": {"VolumeSize": 300}}
            ],
            "TagSpecifications": [
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "anyscale-user", "Value": "aguo@anyscale.com"}],
                }
            ],
            "IamInstanceProfile": {"Arn": "arn:aws:iam:test1234"},
            "NetworkInterfaces": [
                {
                    "Groups": ["sg-1", "sg-2"],
                    "SubnetId": "subnet-1234",
                    "AssociatePublicIpAddress": True,
                }
            ],
        },
    )


def test_convert_cluster_env(mock_auth_api_client) -> None:
    config_controller = ConfigController()
    # config_controller._select_base_image = Mock()
    # config_controller._select_base_image.return_value = "anyscale/ray:test-image"

    cluster_yaml = {
        "setup_commands": ["cmd_1", "cmd_2", "cmd_3"],
        "file_mounts": {"remote_path": "local_path"},
    }

    with patch.object(
        config_controller, "_select_base_image"
    ) as mock_select_base_image:
        mock_select_base_image.return_value = "anyscale/ray:test-image"
        cluster_env_result = config_controller._convert_cluster_env(
            cluster_yaml, True, False
        )
        mock_select_base_image.assert_called_once_with(True, False)

    assert (
        cluster_env_result.to_dict()
        == AppConfigConfigSchema(
            base_image="anyscale/ray:test-image",
            post_build_cmds=["cmd_1", "cmd_2", "cmd_3"],
            python={"pip_packages": [], "conda_packages": []},
            debian_packages=[],
            env_vars={},
        ).to_dict()
    )


@pytest.mark.parametrize(
    "python_version,ray_version,ml,gpu,expected_image",
    [
        ("3.6", "1.6.0", True, True, "anyscale/ray-ml:1.6.0-py36-gpu"),
        ("3.7", "1.6.0", False, False, "anyscale/ray:1.6.0-py37"),
        ("3.8", "1.6.0", True, False, "anyscale/ray-ml:1.6.0-py38"),
        ("3.7", "2.0.0dev0", False, True, "anyscale/ray:1.6.0-py37-gpu"),
    ],
)
def test_select_base_image(
    python_version: str,
    ray_version: str,
    ml: bool,
    gpu: bool,
    expected_image: str,
    mock_auth_api_client,
) -> None:
    mock_detect_python_minor_version = Mock()
    mock_detect_python_minor_version.return_value = python_version
    mock_detect_ray_version = Mock()
    mock_detect_ray_version.return_value = ray_version, "test-commit"

    config_controller = ConfigController()

    with patch.multiple(
        "anyscale.controllers.config_controller",
        detect_python_minor_version=mock_detect_python_minor_version,
        detect_ray_version=mock_detect_ray_version,
    ):
        assert config_controller._select_base_image(ml, gpu) == expected_image


@pytest.mark.parametrize(
    "python_version,ray_version,ml,gpu,expected_result",
    [
        ("3.6", "1.6.0", True, True, "ANYSCALE_RAY_ML_1_6_0_PY36_GPU"),
        ("3.6", "1.5.2", False, True, "ANYSCALE_RAY_1_5_2_PY36_GPU"),
        ("3.7", "1.6.0", False, False, "ANYSCALE_RAY_1_6_0_PY37"),
        ("3.7", "1.4.1", True, True, "ANYSCALE_RAY_ML_1_4_1_PY37_GPU"),
        ("3.8", "1.6.0", True, False, "ANYSCALE_RAY_ML_1_6_0_PY38"),
        ("3.8", "1.5.2", False, False, "ANYSCALE_RAY_1_5_2_PY38"),
    ],
)
def test_find_enum_name(
    python_version: str,
    ray_version: str,
    ml: bool,
    gpu: bool,
    expected_result,
    mock_auth_api_client,
) -> None:
    config_controller = ConfigController()

    assert (
        config_controller._find_enum_name(python_version, ray_version, ml, gpu)
        == expected_result
    )
    assert hasattr(BASEIMAGESENUM, expected_result)
