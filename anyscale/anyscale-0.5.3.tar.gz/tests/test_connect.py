from datetime import datetime
import inspect
import logging
import os
from pathlib import Path
import platform
from typing import Any, Callable, Dict, List, Optional, Tuple
from unittest.mock import ANY, Mock, patch

from packaging import version
import pytest
import ray
import requests

import anyscale
from anyscale.client.openapi_client import SessionListResponse
from anyscale.client.openapi_client.models.app_config import AppConfig
from anyscale.client.openapi_client.models.build import Build
from anyscale.client.openapi_client.models.project import Project
from anyscale.client.openapi_client.models.project_response import ProjectResponse
from anyscale.client.openapi_client.models.session import Session
from anyscale.connect import _is_in_shell, ClientBuilder
from anyscale.sdk.anyscale_client import ComputeTemplateConfig
from anyscale.util import get_wheel_url
from anyscale.utils.connect_helpers import (
    AnyscaleClientConnectResponse,
    AnyscaleClientContext,
)
import anyscale.utils.runtime_env


RAY_VERSION = "1.6.0"
RAY_COMMIT = "7916500c43de46721c51e6b95fb51cfa2c6078ba"


def _make_session(i: int, state: str, cloud_id: str = None) -> Session:
    sess = Session(
        id="session_id",
        name="cluster-{}".format(i),
        created_at=datetime.now(),
        ray_dashboard_url="https://fake_dashboard.com",
        snapshots_history=[],
        idle_timeout=120,
        tensorboard_available=False,
        project_id="project_id",
        state=state,
        cloud_id=cloud_id,
        service_proxy_url="http://session-{}.userdata.com/auth?token=value&bar".format(
            i
        ),
        connect_url="session-{}.userdata.com:8081?port=10001".format(i),
        jupyter_notebook_url="http://session-{}.userdata.com/jupyter/lab?token=value".format(
            i
        ),
        access_token="value",
        host_name="https://session-{}.userdata.com".format(i),
    )
    sess.build_id = "build_id"
    sess.compute_template_id = "mock_compute_template_id"
    return sess


def _make_app_template() -> AppConfig:
    return AppConfig(
        project_id="project_id",
        id="application_template_id",
        name="test-app-config",
        creator_id="creator_id",
        organization_id="organization_id",
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
    )


def _make_build() -> Build:
    return Build(
        id="build_id",
        revision=0,
        application_template_id="application_template_id",
        config_json="",
        creator_id="creator_id",
        status="succeeded",
        created_at=datetime.now(),
        last_modified_at=datetime.now(),
        docker_image_name="docker_image_name",
    )


def _make_compute_template_config() -> ComputeTemplateConfig:

    return ComputeTemplateConfig(
        **{
            "cloud_id": "fake-cloud-id",
            "region": "fake-region",
            "allowed_azs": ["fake-az1"],
            "head_node_type": {
                "name": "head-node-name",
                "instance_type": "fake-head-instance-type",
                "resources": {
                    "cpu": 3,
                    "object_store_memory": 5,
                    "custom_resources": {
                        "custom_resource_1": 10,
                        "custom_resource_2": 12,
                    },
                },
            },
            "worker_node_types": [
                {
                    "name": "worker-node-name",
                    "instance_type": "fake-worker-instance-type",
                    "min_workers": 0,
                    "max_workers": 10,
                    "use_spot": True,
                    "resources": {"cpu": 7, "memory": 11},
                }
            ],
            "aws": {
                "SubnetId": "fake-subnet-id",
                "SecurityGroupIds": ["fake-security-group-id"],
                "IamInstanceProfile": {"Arn": "fake-iam-arn"},
                "TagSpecifications": [
                    {
                        "ResourceType": "instance",
                        "Tags": [{"Key": "fake-key", "Value": "fake-value"}],
                    },
                ],
            },
        }
    )


def _connected(ray: Mock, ret: Dict[str, Any],) -> Callable[[Any, Any], Dict[str, Any]]:
    def connected(*a: Any, **kw: Any) -> Dict[str, Any]:
        ray.util.client.ray.is_connected.return_value = True
        returnable = {
            "num_clients": 1,
            "ray_version": RAY_VERSION,
            "ray_commit": RAY_COMMIT,
            "python_version": platform.python_version(),
            "protocol_version": "fake_version",
        }
        returnable.update(**ret)
        return returnable

    return connected


@pytest.fixture()
def mock_auth_api_client(
    base_mock_api_client: Mock, base_mock_anyscale_api_client: Mock
):
    mock_auth_api_client = Mock(
        api_client=base_mock_api_client,
        anyscale_api_client=base_mock_anyscale_api_client,
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=mock_auth_api_client),
    ):
        yield


@pytest.fixture()
def mock_get_project_block():
    mock_get_project_block = Mock(return_value=Mock())
    with patch.multiple(
        "anyscale.connect_utils.project", ProjectBlock=mock_get_project_block,
    ):
        yield mock_get_project_block


@pytest.fixture()
def mock_get_prepare_cluster_block():
    mock_get_prepare_cluster_block = Mock(return_value=Mock())
    with patch.multiple(
        "anyscale.connect_utils.prepare_cluster",
        PrepareClusterBlock=mock_get_prepare_cluster_block,
    ):
        yield mock_get_prepare_cluster_block


@pytest.fixture()
def mock_get_start_interactive_session_block():
    mock_get_start_interactive_session_block = Mock(return_value=Mock())
    with patch.multiple(
        "anyscale.connect_utils.start_interactive_session",
        StartInteractiveSessionBlock=mock_get_start_interactive_session_block,
    ):
        yield mock_get_start_interactive_session_block


def _make_test_builder(
    tmp_path: Path,
    session_states: Optional[List[str]] = None,
    setup_project_dir: bool = True,
    create_build: bool = True,
    cloud_id: str = None,
) -> Tuple[Any, Any, Any, Any]:
    if session_states is None:
        session_states = ["Running"]

    scratch = tmp_path / "scratch"
    sdk = Mock()
    sess_resp = Mock()
    ray = Mock()

    ray.__commit__ = RAY_COMMIT
    ray.__version__ = RAY_VERSION
    ray.util.client.ray.is_connected.return_value = False
    anyscale.utils.runtime_env.runtime_env_setup = Mock()

    def disconnected(*a: Any, **kw: Any) -> None:
        ray.util.client.ray.is_connected.return_value = False

    # Emulate session lock failure.
    ray.util.connect.side_effect = _connected(ray, {"num_clients": 1})
    ray.util.disconnect.side_effect = disconnected
    job_config_mock = Mock()
    job_config_mock.runtime_env = {}
    job_config_mock.set_runtime_env.return_value = Mock()
    job_config_mock.metadata = {}
    ray.job_config.JobConfig.return_value = job_config_mock
    sess_resp.results = [
        _make_session(i, state, cloud_id) for i, state in enumerate(session_states)
    ]
    sess_resp.metadata.next_paging_token = None
    sdk.list_sessions.return_value = sess_resp
    sdk.search_sessions.return_value = sess_resp
    proj_resp = Mock()
    proj_resp.result.name = "scratch"
    sdk.get_project.return_value = proj_resp
    sdk.get_build = Mock(return_value=Mock(result=_make_build()))
    subprocess = Mock()
    _os = Mock()
    _api_client = Mock()
    _api_client.get_user_info_api_v2_userinfo_get.return_value.result = Mock(
        organizations=[Mock(default_cloud_id=None)]
    )
    _api_client.get_default_cluster_env_build_api_v2_builds_default_py_version_ray_version_get = Mock(
        return_value=Mock(result=_make_build())
    )
    _anyscale_api_client = Mock()
    _auth_api_client = Mock(
        api_client=_api_client, anyscale_api_client=_anyscale_api_client
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=_auth_api_client),
    ):
        builder = ClientBuilder(
            anyscale_sdk=sdk,
            subprocess=subprocess,
            _ray=ray,
            _os=_os,
            _ignore_version_check=False,
            auth_api_client=_auth_api_client,
        )
    builder._exec_controller.api_client = _api_client
    builder._exec_controller.anyscale_api_client = _anyscale_api_client
    builder._session_controller.api_client = _api_client
    builder._session_controller.anyscale_api_client = _anyscale_api_client
    if setup_project_dir:
        builder.project_dir(scratch.absolute().as_posix())
    else:
        builder._in_shell = True
    sdk.search_projects = lambda _: SessionListResponse(results=[])
    builder._find_project_id = lambda _: None  # type: ignore

    def create_session(*a: Any, **kw: Any) -> None:
        sess_resp.results = sess_resp.results + [
            _make_session(len(sess_resp.results), "Running")
        ]
        sdk.list_sessions.return_value = sess_resp

    setattr(builder, "_start_session", Mock())
    builder._start_session.side_effect = create_session  # type: ignore
    builder._register_compute_template = Mock(return_value="mock_compute_template_id")  # type: ignore

    setattr(
        builder, "_get_last_used_cloud", Mock(return_value="anyscale_default_cloud")
    )

    if create_build:
        _make_app_template()
        mock_build = _make_build()
        builder._get_cluster_env_build = Mock(return_value=mock_build)  # type: ignore

    return builder, sdk, subprocess, ray


def test_parse_address(mock_auth_api_client) -> None:
    """Tests ClientBuilder._parse_address which parses the anyscale address."""

    sdk = Mock()
    _api_client = Mock()
    connect_instance = ClientBuilder(
        anyscale_sdk=sdk,
        auth_api_client=Mock(api_client=_api_client, anyscale_api_client=Mock()),
    )

    connect_instance._parse_address(None)
    assert connect_instance._cluster_name is None
    assert connect_instance._autosuspend_timeout is None
    assert connect_instance._cluster_compute_name is None
    assert connect_instance._cluster_env_name is None

    connect_instance._parse_address("")
    assert connect_instance._cluster_name is None
    assert connect_instance._autosuspend_timeout is None
    assert connect_instance._cluster_compute_name is None
    assert connect_instance._cluster_env_name is None

    connect_instance._parse_address("cluster_name")
    assert connect_instance._cluster_name == "cluster_name"
    assert connect_instance._autosuspend_timeout is None
    assert connect_instance._cluster_compute_name is None
    assert connect_instance._cluster_env_name is None

    connect_instance._parse_address(
        "my_cluster?cluster_compute=my_template&autosuspend=5&cluster_env=bla:1&update=True"
    )
    assert connect_instance._cluster_name == "my_cluster"
    assert connect_instance._autosuspend_timeout == 5
    assert connect_instance._cluster_compute_name == "my_template"
    assert connect_instance._cluster_env_name == "bla"
    assert connect_instance._needs_update

    with pytest.raises(ValueError):
        # we only support cluster_compute, cluster_env, autosuspend
        connect_instance._parse_address("my_cluster?random=5")


def test_cloud_from_env(mock_auth_api_client) -> None:
    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder.cloud("explicit_cloud")

    with patch.dict(os.environ, {"ANYSCALE_CLOUD": "env_cloud"}):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._cloud_name == "env_cloud"
        configured_builder._fill_unset_configs_from_env()
        assert configured_builder._cloud_name == "explicit_cloud"


def test_autosuspend_init_args(mock_auth_api_client) -> None:
    builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    builder._init_args()
    assert builder._autosuspend_timeout is None
    builder._init_args(autosuspend="20")
    assert builder._autosuspend_timeout == 20
    builder._init_args(autosuspend=20)
    assert builder._autosuspend_timeout == 20  # 20 minutes
    builder._init_args(autosuspend="20m")
    assert builder._autosuspend_timeout == 20
    builder._init_args(autosuspend="3h")
    assert builder._autosuspend_timeout == 180  # 3 hours
    builder._init_args(autosuspend="-1")
    assert builder._autosuspend_timeout == -1  # disabled
    builder._init_args(autosuspend=-1)
    assert builder._autosuspend_timeout == -1  # disabled


def test_autosuspend_from_env(mock_auth_api_client) -> None:
    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    unconfigured_builder._fill_unset_configs_from_env()
    assert unconfigured_builder._autosuspend_timeout == 120  # default

    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder._parse_autosuspend(-1)

    with patch.dict(os.environ, {"ANYSCALE_AUTOSUSPEND": "20"}):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._autosuspend_timeout == 20
        configured_builder._fill_unset_configs_from_env()
        assert configured_builder._autosuspend_timeout == -1

    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    with patch.dict(os.environ, {"ANYSCALE_AUTOSUSPEND": "10h"}):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._autosuspend_timeout == 600  # 600 mins

    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    with patch.dict(os.environ, {"ANYSCALE_AUTOSUSPEND": "10m"}):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._autosuspend_timeout == 10  # 10 mins

    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    with patch.dict(os.environ, {"ANYSCALE_AUTOSUSPEND": "-1"}):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._autosuspend_timeout == -1  # disabled


def test_cluster_compute_from_env(mock_auth_api_client) -> None:
    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder.cluster_compute("explicit_compute")

    # cluster compute can be explicitly configured with either dict or string
    configured_builder_2 = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder_2.cluster_compute({"cloud_id": "123"})

    with patch.dict(os.environ, {"ANYSCALE_CLUSTER_COMPUTE": "env_compute"}):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._cluster_compute_name == "env_compute"
        assert unconfigured_builder._cluster_compute_dict is None
        configured_builder._fill_unset_configs_from_env()
        assert configured_builder._cluster_compute_name == "explicit_compute"
        assert configured_builder._cluster_compute_dict is None
        configured_builder_2._fill_unset_configs_from_env()
        assert configured_builder_2._cluster_compute_name is None
        assert configured_builder_2._cluster_compute_dict == {"cloud_id": "123"}


def test_cluster_env_from_env(mock_auth_api_client) -> None:
    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder.cluster_env("explicit_env")

    # cluster env can be explicitly configured with either dict or string
    configured_builder_2 = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder_2.cluster_env({"base_image": "some/image"})

    with patch.dict(os.environ, {"ANYSCALE_CLUSTER_ENV": "env_cluster_env"}):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._cluster_env_name == "env_cluster_env"
        assert unconfigured_builder._cluster_env_dict is None
        configured_builder._fill_unset_configs_from_env()
        assert configured_builder._cluster_env_name == "explicit_env"
        assert configured_builder._cluster_env_dict is None
        configured_builder_2._fill_unset_configs_from_env()
        assert configured_builder_2._cluster_env_name is None
        assert configured_builder_2._cluster_env_dict == {"base_image": "some/image"}


def test_job_name_from_env(mock_auth_api_client) -> None:
    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder.job_name("explicit_job_name")

    with patch.dict(os.environ, {"ANYSCALE_JOB_NAME": "env_job_name"}):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._job_config.metadata["job_name"] == "env_job_name"
        configured_builder._fill_unset_configs_from_env()
        assert (
            configured_builder._job_config.metadata["job_name"] == "explicit_job_name"
        )


def test_namespace_from_env(mock_auth_api_client) -> None:
    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    configured_builder.namespace("explicit_namespace")

    with patch.dict(os.environ, {"ANYSCALE_NAMESPACE": "env_namespace"}):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._job_config.ray_namespace == "env_namespace"
        configured_builder._fill_unset_configs_from_env()
        assert configured_builder._job_config.ray_namespace == "explicit_namespace"


def test_multiple_env_configs(mock_auth_api_client) -> None:
    unconfigured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    partially_configured_builder = ClientBuilder(
        anyscale_sdk=Mock(),
        auth_api_client=Mock(api_client=Mock(), anyscale_api_client=Mock()),
    )
    partially_configured_builder.namespace("explicit_namespace")
    with patch.dict(
        os.environ,
        {"ANYSCALE_NAMESPACE": "env_namespace", "ANYSCALE_CLOUD": "env_cloud"},
    ):
        unconfigured_builder._fill_unset_configs_from_env()
        assert unconfigured_builder._job_config.ray_namespace == "env_namespace"
        assert unconfigured_builder._cloud_name == "env_cloud"
        partially_configured_builder._fill_unset_configs_from_env()
        assert (
            partially_configured_builder._job_config.ray_namespace
            == "explicit_namespace"
        )
        assert partially_configured_builder._cloud_name == "env_cloud"


def test_new_proj_connect_params(
    tmp_path: Path,
    mock_auth_api_client,
    mock_get_project_block,
    mock_get_prepare_cluster_block,
    mock_get_start_interactive_session_block,
) -> None:
    project_dir = (tmp_path / "my_proj").absolute().as_posix()
    builder, _, _, _ = _make_test_builder(tmp_path)
    mock_cluster = builder._anyscale_sdk.search_sessions.return_value.results[0]

    mock_project_block = mock_get_project_block.return_value
    mock_project_block.project_dir = project_dir
    mock_prepare_cluster_block = mock_get_prepare_cluster_block.return_value
    mock_prepare_cluster_block.cluster_name = mock_cluster.name

    builder.project_dir(project_dir).connect()

    mock_get_project_block.assert_called_once_with(
        project_dir=project_dir, project_name=None
    )
    mock_get_prepare_cluster_block.assert_called_once_with(
        allow_public_internet_traffic=builder._allow_public_internet_traffic,
        autosuspend_timeout=builder._autosuspend_timeout,
        build_commit=builder._build_commit,
        build_pr=builder._build_pr,
        cloud_name=builder._cloud_name,
        cluster_compute_dict=builder._cluster_compute_dict,
        cluster_compute_name=builder._cluster_compute_name,
        cluster_env_dict=builder._cluster_env_dict,
        cluster_env_name=builder._cluster_env_name,
        cluster_env_revision=builder._cluster_env_revision,
        cluster_name=builder._cluster_name,
        force_rebuild=builder._force_rebuild,
        needs_update=builder._needs_update,
        project_id=mock_project_block.project_id,
        ray=builder._ray,
    )
    mock_get_start_interactive_session_block.assert_called_once_with(
        cluster=mock_cluster,
        job_config=builder._job_config,
        allow_multiple_clients=False,
        initial_scale=builder._initial_scale,
        in_shell=builder._in_shell,
        run_mode=builder._run_mode,
        ray_init_kwargs=builder._ray_init_kwargs,
        secure=builder._secure,
        ignore_version_check=builder._ignore_version_check,
        ray=builder._ray,
        subprocess=builder._subprocess,
    )


def test_background_run_mode(
    tmp_path: Path,
    mock_auth_api_client,
    mock_get_project_block,
    mock_get_prepare_cluster_block,
    mock_get_start_interactive_session_block,
) -> None:
    scratch_dir = (tmp_path / "scratch").absolute().as_posix()
    # Making scratch dir because get_project_block is mocked out
    os.mkdir(scratch_dir)
    builder, _, _, _ = _make_test_builder(tmp_path)
    builder._session_controller.push = Mock()
    builder._exec_controller.anyscale_exec = Mock()
    mock_cluster = builder._anyscale_sdk.search_sessions.return_value.results[0]
    mock_get_prepare_cluster_block.return_value.cluster_name = mock_cluster.name
    builder._cluster_name = mock_cluster.name
    mock_get_project_block.return_value.project_dir = scratch_dir

    # Should create a new .anyscale.yaml file in the scratch dir
    builder.run_mode("background").connect()

    builder._session_controller.push.assert_called_with(
        "cluster-0", all_nodes=False, config=None, source=ANY, target=ANY
    )
    builder._exec_controller.anyscale_exec.assert_called_with(
        "cluster-0",
        commands=ANY,
        port_forward=(),
        screen=False,
        stop=False,
        sync=False,
        terminate=False,
        tmux=False,
    )
    builder._os._exit.assert_called_once_with(0)


def test_local_docker_run_mode(
    tmp_path: Path,
    mock_auth_api_client,
    mock_get_project_block,
    mock_get_prepare_cluster_block,
    mock_get_start_interactive_session_block,
) -> None:
    scratch_dir = (tmp_path / "scratch").absolute().as_posix()
    # Making scratch dir because get_project_block is mocked out
    os.mkdir(scratch_dir)
    builder, _, subprocess, _ = _make_test_builder(tmp_path)
    mock_cluster = builder._anyscale_sdk.search_sessions.return_value.results[0]
    mock_get_prepare_cluster_block.return_value.cluster_name = mock_cluster.name
    mock_get_project_block.return_value.project_dir = scratch_dir

    builder.run_mode("local_docker").connect()

    subprocess.check_call.assert_called_with(
        [
            "docker",
            "run",
            "--env",
            ANY,
            "--env",
            ANY,
            "-v",
            ANY,
            "--entrypoint=/bin/bash",
            ANY,
            "-c",
            ANY,
        ]
    )
    builder._os._exit.assert_called_once_with(0)


def test_connect_with_cloud(
    tmp_path: Path,
    mock_auth_api_client,
    mock_get_project_block,
    mock_get_prepare_cluster_block,
    mock_get_start_interactive_session_block,
) -> None:
    scratch_dir = (tmp_path / "scratch").absolute().as_posix()
    builder, _, _, _ = _make_test_builder(tmp_path)
    mock_cluster = builder._anyscale_sdk.search_sessions.return_value.results[0]
    mock_get_prepare_cluster_block.return_value.cluster_name = mock_cluster.name
    mock_get_project_block.return_value.project_dir = scratch_dir

    builder.session(mock_cluster.name).cloud("test_cloud").connect()

    assert builder._cloud_name == "test_cloud"

    mock_get_prepare_cluster_block.assert_called_once_with(
        allow_public_internet_traffic=builder._allow_public_internet_traffic,
        autosuspend_timeout=builder._autosuspend_timeout,
        build_commit=builder._build_commit,
        build_pr=builder._build_pr,
        cloud_name=builder._cloud_name,
        cluster_compute_dict=builder._cluster_compute_dict,
        cluster_compute_name=builder._cluster_compute_name,
        cluster_env_dict=builder._cluster_env_dict,
        cluster_env_name=builder._cluster_env_name,
        cluster_env_revision=builder._cluster_env_revision,
        cluster_name=builder._cluster_name,
        force_rebuild=builder._force_rebuild,
        needs_update=builder._needs_update,
        project_id=mock_get_project_block.return_value.project_id,
        ray=builder._ray,
    )


def test_connect_with_cluster_env_dict(
    tmp_path: Path,
    mock_auth_api_client,
    mock_get_project_block,
    mock_get_prepare_cluster_block,
    mock_get_start_interactive_session_block,
) -> None:
    scratch_dir = (tmp_path / "scratch").absolute().as_posix()
    builder, _, _, _ = _make_test_builder(tmp_path)
    mock_cluster = builder._anyscale_sdk.search_sessions.return_value.results[0]
    mock_get_prepare_cluster_block.return_value.cluster_name = mock_cluster.name
    mock_get_project_block.return_value.project_dir = scratch_dir

    cluster_env_dict = {
        "name": "my_cluster_env",
        "base_image": "anyscale/ray:1.4.0-py37",
    }
    builder.cluster_env(cluster_env_dict).connect()

    assert builder._cluster_env_dict == {"base_image": "anyscale/ray:1.4.0-py37"}
    assert builder._cluster_env_name == "my_cluster_env"

    mock_get_prepare_cluster_block.assert_called_once_with(
        allow_public_internet_traffic=builder._allow_public_internet_traffic,
        autosuspend_timeout=builder._autosuspend_timeout,
        build_commit=builder._build_commit,
        build_pr=builder._build_pr,
        cloud_name=builder._cloud_name,
        cluster_compute_dict=builder._cluster_compute_dict,
        cluster_compute_name=builder._cluster_compute_name,
        cluster_env_dict=builder._cluster_env_dict,
        cluster_env_name=builder._cluster_env_name,
        cluster_env_revision=builder._cluster_env_revision,
        cluster_name=builder._cluster_name,
        force_rebuild=builder._force_rebuild,
        needs_update=builder._needs_update,
        project_id=mock_get_project_block.return_value.project_id,
        ray=builder._ray,
    )


def test_base_docker_image(tmp_path: Path, project_test_data: Project,) -> None:
    scratch_dir = (tmp_path / "scratch").absolute().as_posix()
    builder, _, _, _ = _make_test_builder(tmp_path, session_states=["Running"])

    # Base docker images are no longer supported
    with pytest.raises(ValueError):
        builder.project_dir(scratch_dir).base_docker_image(
            "anyscale/ray-ml:custom"
        ).connect()


def test_requirements_list(tmp_path: Path, project_test_data: Project) -> None:
    builder, _, _, _ = _make_test_builder(tmp_path, session_states=[])

    # anyscale.require().connect() no longer supported
    with pytest.raises(ValueError):
        builder.require(["pandas", "wikipedia"]).connect()


def test_disable_cloud_change(tmp_path: Path, project_test_data: Project) -> None:
    builder, sdk, _, ray = _make_test_builder(
        tmp_path=tmp_path, cloud_id="test_cloud_1"
    )
    sdk.create_project.return_value = ProjectResponse(result=project_test_data)
    ray.util.disconnect()
    with pytest.raises(Exception):
        builder.session("cluster-0", update=True).cloud("test_cloud_2").connect()


@pytest.mark.parametrize("enable_multiple_clients", [True, False])
def test_multiple_clients(
    enable_multiple_clients: bool,
    tmp_path: Path,
    mock_auth_api_client,
    mock_get_project_block,
    mock_get_prepare_cluster_block,
    mock_get_start_interactive_session_block,
) -> None:
    try:
        os.environ["ANYSCALE_ALLOW_MULTIPLE_CLIENTS"] = (
            "1" if enable_multiple_clients else "0"
        )
        builder, _, _, _ = _make_test_builder(tmp_path)
        scratch_dir = (tmp_path / "scratch").absolute().as_posix()
        mock_cluster = builder._anyscale_sdk.search_sessions.return_value.results[0]
        mock_get_prepare_cluster_block.return_value.cluster_name = mock_cluster.name
        mock_get_project_block.return_value.project_dir = scratch_dir

        builder.session("cluster-0", update=False).connect()
        mock_get_start_interactive_session_block.assert_called_once_with(
            cluster=mock_cluster,
            job_config=builder._job_config,
            allow_multiple_clients=enable_multiple_clients,
            initial_scale=builder._initial_scale,
            in_shell=builder._in_shell,
            run_mode=builder._run_mode,
            ray_init_kwargs=builder._ray_init_kwargs,
            secure=builder._secure,
            ignore_version_check=builder._ignore_version_check,
            ray=builder._ray,
            subprocess=builder._subprocess,
        )

    finally:
        del os.environ["ANYSCALE_ALLOW_MULTIPLE_CLIENTS"]


class MockPopen(object):
    def __init__(self) -> None:
        self.returncode = 0

    def communicate(self) -> Tuple[str, str]:
        return (
            '[{"id": "cloud2", "name": "second cloud"}, {"id": "cloud1", "name": "first cloud"}]',
            "",
        )


@pytest.mark.parametrize(
    "ray_version_tuple",
    [
        ["COMMIT_ID", "2.0.0.dev0", "master/COMMIT_ID/ray-2.0.0.dev0"],
        ["RELEASE_COMMIT_ID", "1.4.0", "releases/1.4.0/RELEASE_COMMIT_ID/ray-1.4.0"],
    ],
)
@pytest.mark.parametrize("py_version", ["36", "37", "38"])
def test_get_wheel_url(py_version, ray_version_tuple) -> None:
    commit_id, ray_version, expected_suffix = ray_version_tuple
    wheel_prefix = f"https://s3-us-west-2.amazonaws.com/ray-wheels/{expected_suffix}"

    expected_py_version = f"cp{py_version}-cp{py_version}m"

    if py_version == "38":
        expected_py_version = expected_py_version.rstrip("m")

    if py_version == "38":
        expected_macos_wheel = (
            f"{wheel_prefix}-{expected_py_version}-macosx_10_15_x86_64.whl"
        )
    else:
        expected_macos_wheel = (
            f"{wheel_prefix}-{expected_py_version}-macosx_10_15_intel.whl"
        )

    assert (
        get_wheel_url(commit_id, ray_version, py_version, "darwin")
        == expected_macos_wheel
    )

    assert (
        get_wheel_url(commit_id, ray_version, py_version, "linux")
        == f"{wheel_prefix}-{expected_py_version}-manylinux2014_x86_64.whl"
    )

    assert (
        get_wheel_url(commit_id, ray_version, py_version, "win32")
        == f"{wheel_prefix}-{expected_py_version}-win_amd64.whl"
    )


def test_commit_url_is_valid() -> None:
    for python_version in ["36", "37", "38"]:
        for pltfrm in ["win32", "linux", "darwin"]:
            url = get_wheel_url(RAY_COMMIT, RAY_VERSION, python_version, pltfrm)
            # We use HEAD, because it is faster than downloading with GET
            resp = requests.head(url)
            assert resp.status_code == 200, f"Cannot find wheel for: {url}"


def test_set_metadata_in_job_config(mock_auth_api_client) -> None:
    sdk = Mock()
    _api_client = Mock()
    _api_client.get_user_info_api_v2_userinfo_get = Mock(
        return_value=Mock(result=Mock(id="mock_creator_id"))
    )

    def mock_set_metadata(key: str, val: str) -> None:
        connect_instance._job_config.metadata[key] = val

    # Test no user specified job name, user specified creator_id
    connect_instance = ClientBuilder(
        anyscale_sdk=sdk,
        auth_api_client=Mock(api_client=_api_client, anyscale_api_client=Mock()),
    )
    connect_instance._job_config.metadata = {}
    connect_instance._job_config.set_metadata = mock_set_metadata
    with patch("sys.argv", new=["file_name"]):
        connect_instance._set_metadata_in_job_config("mock_creator_id")
    assert connect_instance._job_config.metadata["job_name"].startswith("file_name")
    assert connect_instance._job_config.metadata["creator_id"] == "mock_creator_id"

    # Test no user specified job name
    connect_instance = ClientBuilder(
        anyscale_sdk=sdk,
        auth_api_client=Mock(api_client=_api_client, anyscale_api_client=Mock()),
    )
    connect_instance._job_config.metadata = {}
    connect_instance._job_config.set_metadata = mock_set_metadata
    with patch("sys.argv", new=["file_name"]):
        connect_instance._set_metadata_in_job_config()
    assert connect_instance._job_config.metadata["job_name"].startswith("file_name")
    assert connect_instance._job_config.metadata["creator_id"] == "mock_creator_id"

    # Test user specified job name
    connect_instance = ClientBuilder(
        anyscale_sdk=sdk,
        auth_api_client=Mock(api_client=_api_client, anyscale_api_client=Mock()),
    )
    connect_instance._job_config.metadata = {}
    connect_instance._job_config.set_metadata = mock_set_metadata
    connect_instance.job_name("mock_job_name")._set_metadata_in_job_config()
    assert connect_instance._job_config.metadata["job_name"].startswith("mock_job_name")
    assert connect_instance._job_config.metadata["creator_id"] == "mock_creator_id"


def test_namespace(mock_auth_api_client) -> None:
    sdk = Mock()
    _api_client = Mock()

    # Test no user specified job name
    connect_instance = ClientBuilder(
        anyscale_sdk=sdk,
        auth_api_client=Mock(api_client=_api_client, anyscale_api_client=Mock()),
    )

    def mock_set_ray_namespace(namespace: str) -> None:
        connect_instance._job_config.ray_namespace = namespace

    connect_instance._job_config.set_ray_namespace = mock_set_ray_namespace
    connect_instance.namespace("mock_namespace")
    assert connect_instance._job_config.ray_namespace == "mock_namespace"


def test_set_runtime_env_in_job_config(
    tmp_path: Path,
    mock_auth_api_client,
    mock_get_project_block,
    mock_get_prepare_cluster_block,
    mock_get_start_interactive_session_block,
) -> None:

    sdk = Mock()
    _api_client = Mock()
    connect_instance = ClientBuilder(
        anyscale_sdk=sdk,
        auth_api_client=Mock(api_client=_api_client, anyscale_api_client=Mock()),
    )
    connect_instance.env({"working_dir": "/tmp"})._set_runtime_env_in_job_config("/")
    assert connect_instance._job_config.runtime_env["working_dir"] == "/tmp"
    assert connect_instance._job_config.runtime_env["excludes"] == [
        ".git",
        "__pycache__",
        "venv",
        "/.anyscale.yaml",
        "/session-default.yaml",
    ]

    connect_instance = ClientBuilder(
        anyscale_sdk=sdk,
        auth_api_client=Mock(api_client=_api_client, anyscale_api_client=Mock()),
    )
    connect_instance.env({})._set_runtime_env_in_job_config("/tmp")
    assert connect_instance._job_config.runtime_env["working_dir"] == "/tmp"
    assert connect_instance._job_config.runtime_env["excludes"] == [
        ".git",
        "__pycache__",
        "venv",
        "/tmp/.anyscale.yaml",
        "/tmp/session-default.yaml",
    ]

    connect_instance = ClientBuilder(
        anyscale_sdk=sdk,
        auth_api_client=Mock(api_client=_api_client, anyscale_api_client=Mock()),
    )
    connect_instance.env(
        {"working_dir": "/tmp", "excludes": [".gitignore"], "pip": ["numpy"]}
    )._set_runtime_env_in_job_config("/")
    assert connect_instance._job_config.runtime_env["working_dir"] == "/tmp"
    assert connect_instance._job_config.runtime_env["excludes"] == [
        ".git",
        "__pycache__",
        "venv",
        ".gitignore",
        "/.anyscale.yaml",
        "/session-default.yaml",
    ]
    assert connect_instance._job_config.runtime_env["pip"] == ["numpy"]

    proj_dir = "/tmp"
    connect_instance, _, _, _ = _make_test_builder(tmp_path)
    mock_cluster = connect_instance._anyscale_sdk.search_sessions.return_value.results[
        0
    ]
    mock_get_prepare_cluster_block.return_value.cluster_name = mock_cluster.name
    mock_get_project_block.return_value.project_dir = proj_dir

    connect_instance.env({"working_dir": "/tmp"}).project_dir("/tmp").connect()
    connect_instance._job_config.set_runtime_env.assert_called_once_with(  # type: ignore
        {
            "working_dir": "/tmp",
            "excludes": [
                ".git",
                "__pycache__",
                "venv",
                "/tmp/.anyscale.yaml",
                "/tmp/session-default.yaml",
            ],
            "env_vars": {"RAY_SERVE_ROOT_URL": "https://serve-session-0.userdata.com"},
        }
    )
    mock_get_prepare_cluster_block.assert_called_once_with(
        allow_public_internet_traffic=connect_instance._allow_public_internet_traffic,
        autosuspend_timeout=connect_instance._autosuspend_timeout,
        build_commit=connect_instance._build_commit,
        build_pr=connect_instance._build_pr,
        cloud_name=connect_instance._cloud_name,
        cluster_compute_dict=connect_instance._cluster_compute_dict,
        cluster_compute_name=connect_instance._cluster_compute_name,
        cluster_env_dict=connect_instance._cluster_env_dict,
        cluster_env_name=connect_instance._cluster_env_name,
        cluster_env_revision=connect_instance._cluster_env_revision,
        cluster_name=connect_instance._cluster_name,
        force_rebuild=connect_instance._force_rebuild,
        needs_update=connect_instance._needs_update,
        project_id=mock_get_project_block.return_value.project_id,
        ray=connect_instance._ray,
    )
    mock_get_start_interactive_session_block.assert_called_once_with(
        cluster=mock_cluster,
        job_config=connect_instance._job_config,
        allow_multiple_clients=False,
        initial_scale=connect_instance._initial_scale,
        in_shell=connect_instance._in_shell,
        run_mode=connect_instance._run_mode,
        ray_init_kwargs=connect_instance._ray_init_kwargs,
        secure=connect_instance._secure,
        ignore_version_check=connect_instance._ignore_version_check,
        ray=connect_instance._ray,
        subprocess=connect_instance._subprocess,
    )


@patch.dict(
    os.environ,
    {
        "ANYSCALE_SESSION_ID": "ses_fake-session-01234567890",
        "RAY_ADDRESS": "anyscale://fake-cluster",
    },
)
def test_runtime_env_set_when_run_on_anyscale_cluster(
    tmp_path: Path, project_test_data: Project
):
    """Test that the runtime env is set when a Ray client script is run on an Anyscale node.

    See https://github.com/anyscale/product/issues/6809.
    """
    connect_instance, sdk, _, _ = _make_test_builder(tmp_path, [])
    sdk.create_project.return_value = ProjectResponse(result=project_test_data)

    runtime_env_pip = ["seaborn"]
    connect_instance.env({"pip": runtime_env_pip}).connect()
    connect_instance._job_config.set_runtime_env.assert_called_once_with(  # type: ignore
        {"pip": runtime_env_pip}
    )


@pytest.mark.parametrize(
    "anyscale_call_frames",
    [
        [  # black: no
            "/path/anyscale/connect.py",
            "/path/anyscale/connect.py",
            "/path/anyscale/__init__.py",
        ],
        [  # black: no
            "/path/anyscale/connect.py",
            "/path/anyscale/connect.py",
            "/path/ray/client_builder.py",
            "/path/ray/client_builder.py",
        ],
    ],
)
@pytest.mark.parametrize("file_name", ["random_file.py", "anyscale_in_file_name.py"])
def test_is_in_shell(anyscale_call_frames, file_name) -> None:
    """
    Tests if Anyscale Connect Determines if we are in an interactive
    context for both invocations via anyscale.connect() & ray.init("anyscale://")
    """

    def frame_mock(name: str) -> Any:
        mock = Mock()
        mock.filename = name
        return mock

    ipython_shell = [
        "<ipython-input-2-f869cc61c5de>",
        "/home/ubuntu/anaconda3/envs/anyscale/bin/ipython",
    ]
    assert _is_in_shell(list(map(frame_mock, anyscale_call_frames + ipython_shell)))

    python_shell = ["<stdin>"]
    assert _is_in_shell(list(map(frame_mock, anyscale_call_frames + python_shell)))

    # Running file via `ipython random_file.py`
    ipython_from_file = [
        file_name,
        "/home/ubuntu/anaconda3/envs/anyscale/bin/ipython",
    ]
    assert not _is_in_shell(
        list(map(frame_mock, anyscale_call_frames + ipython_from_file))
    )

    # Running file via `python random_file.py`
    python_from_file = [file_name]
    assert not _is_in_shell(
        list(map(frame_mock, anyscale_call_frames + python_from_file))
    )


def test_multiclient_context() -> None:
    """Test that the correct arguments are passed to Ray ClientContext
    on versions where multiclient is supported.
    """

    # Can't patch __init__ indirectly since it's a magic method, track that
    # methods are called with variables
    multiclient_init_called = False
    no_multiclient_init_called = False

    # Simulates ClientContext.__init__ after changes from
    # https://github.com/ray-project/ray/pull/17942
    def multiclient_init(
        self,
        dashboard_url,
        python_version,
        ray_version,
        ray_commit,
        protocol_version,
        _num_clients,
        _context_to_restore,
    ):
        nonlocal multiclient_init_called
        multiclient_init_called = True

    with patch("ray.client_builder.ClientContext.__init__", multiclient_init):
        AnyscaleClientContext(
            anyscale_cluster_info=AnyscaleClientConnectResponse(cluster_id="cluster-1"),
            python_version=platform.python_version(),
            _num_clients=1,
            ray_version=RAY_VERSION,
            ray_commit=RAY_COMMIT,
            protocol_version="fake_version",
            dashboard_url="https://fake_dashboard.com",
        )
        assert multiclient_init_called

    # Simulates ClientContext.__init__ from before changes from
    # https://github.com/ray-project/ray/pull/17942
    def no_multiclient_init(
        self,
        dashboard_url,
        python_version,
        ray_version,
        ray_commit,
        protocol_version,
        _num_clients,
    ):
        nonlocal no_multiclient_init_called
        no_multiclient_init_called = True

    with patch("ray.client_builder.ClientContext.__init__", no_multiclient_init):
        AnyscaleClientContext(
            anyscale_cluster_info=AnyscaleClientConnectResponse(cluster_id="cluster-1"),
            python_version=platform.python_version(),
            _num_clients=1,
            ray_version=RAY_VERSION,
            ray_commit=RAY_COMMIT,
            protocol_version="fake_version",
            dashboard_url="https://fake_dashboard.com",
        )
        assert no_multiclient_init_called


# ray.init("anyscale://"") only works on Ray 1.5+
init_connect_supported = version.parse(ray.__version__) >= version.parse("1.5")

# Check if ray.util.connect accepts ray_init_kwargs to forward
connect_sig = inspect.signature(ray.util.connect)
forward_init_args_supported = "ray_init_kwargs" in connect_sig.parameters


@pytest.mark.skipif(
    not forward_init_args_supported,
    reason="Forwarding init args isn't supported on this version of ray",
)
@pytest.mark.skipif(
    not init_connect_supported,
    reason="ray.init('anyscale://') isn't supported on this version of ray",
)
def test_forward_argument(mock_auth_api_client) -> None:
    """Tests ClientBuilder._forward_argument."""

    sdk = Mock()
    _api_client = Mock()
    connect_instance = ClientBuilder(
        anyscale_sdk=sdk,
        auth_api_client=Mock(api_client=_api_client, anyscale_api_client=Mock()),
    )

    # Should return false on arguments that aren't part of ray.init
    assert not connect_instance._forward_argument("somarg", 123)

    # Should return true on real arguments
    assert connect_instance._forward_argument("object_store_memory", 98765)
    assert connect_instance._forward_argument("log_to_driver", False)
    assert connect_instance._forward_argument("logging_level", logging.INFO)

    # Check values set properly
    assert connect_instance._ray_init_kwargs["object_store_memory"] == 98765
    assert connect_instance._ray_init_kwargs["log_to_driver"] is False
    assert connect_instance._ray_init_kwargs["logging_level"] == logging.INFO
    assert len(connect_instance._ray_init_kwargs) == 3
