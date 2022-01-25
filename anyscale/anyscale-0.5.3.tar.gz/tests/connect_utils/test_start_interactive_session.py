import json
import logging
from typing import Any, Callable, Dict, Optional
from unittest.mock import ANY, Mock, patch

import pytest

from anyscale.connect_utils.start_interactive_session import (
    INITIAL_SCALE_TYPE,
    StartInteractiveSessionBlock,
)
from anyscale.utils.connect_helpers import (
    AnyscaleClientConnectResponse,
    AnyscaleClientContext,
)


def _connected(ray: Mock, ret: Dict[str, Any],) -> Callable[[Any, Any], Dict[str, Any]]:
    def connected(*a: Any, **kw: Any) -> Dict[str, Any]:
        ray.util.client.ray.is_connected.return_value = True
        returnable = {
            "num_clients": 1,
            "ray_version": "mock_ray_version",
            "ray_commit": "mock_ray_commit",
            "python_version": "mock_python_version",
            "protocol_version": "fake_version",
        }
        returnable.update(**ret)
        return returnable

    return connected


@pytest.fixture
def mock_interactive_session_block():
    with patch.multiple(
        "anyscale.connect_utils.start_interactive_session.StartInteractiveSessionBlock",
        __init__=Mock(return_value=None),
    ):
        interactive_session_block = StartInteractiveSessionBlock()
        interactive_session_block.api_client = Mock()
        interactive_session_block.log = Mock()
        interactive_session_block.block_label = ""
        return interactive_session_block


@pytest.mark.parametrize(
    "jobs_resp", [Mock(results=[]), Mock(results=[Mock(id="mock_job_id")])]
)
def test_log_interactive_session_info(mock_interactive_session_block, jobs_resp: Mock):
    mock_interactive_session_block.api_client.list_decorated_jobs_api_v2_decorated_jobs_get = Mock(
        return_value=jobs_resp
    )
    mock_interactive_session_block._log_interactive_session_info(
        "mock_cluster_id",
        "mock_project_id",
        interactive_session_name="mock_interactive_session_name",
    )
    if not len(jobs_resp.results):
        mock_interactive_session_block.log.warning.assert_called_once_with(ANY)
    else:
        mock_interactive_session_block.log.warning.assert_not_called()


def test_acquire_session_lock_success(mock_interactive_session_block):
    """
    Test successful call to _acquire_session_lock.
    """
    mock_interactive_session_block._get_connect_params = Mock(
        return_value=("mock_session_url", "mock_secure", "mock_metadata")
    )
    info = {"num_clients": 0}
    mock_interactive_session_block._ray = Mock()
    mock_interactive_session_block._ray.util.connect = Mock(return_value=info)
    mock_interactive_session_block._ray.util.disconnect = Mock()
    mock_interactive_session_block._dynamic_check = Mock()
    mock_check_required_ray_version = Mock()
    mock_session = Mock()
    mock_session.name = "mock_session_name"
    mock_job_config = Mock()

    with patch.multiple(
        "anyscale.connect_utils.start_interactive_session",
        check_required_ray_version=mock_check_required_ray_version,
    ), patch.multiple(
        "inspect",
        getfullargspec=Mock(return_value=Mock(kwonlyargs=["ray_init_kwargs"])),
    ):
        assert (
            mock_interactive_session_block._acquire_session_lock(
                mock_session, 0, True, False, {}, job_config=mock_job_config
            )
            == info
        )
    mock_interactive_session_block._get_connect_params.assert_called_with(
        mock_session, True
    )
    mock_interactive_session_block._ray.util.connect.assert_called_with(
        "mock_session_url",
        connection_retries=0,
        ignore_version=True,
        job_config=mock_job_config,
        metadata="mock_metadata",
        secure="mock_secure",
        ray_init_kwargs={"logging_level": logging.ERROR},
    )
    mock_interactive_session_block._dynamic_check.assert_called_with(info, False)


@pytest.mark.parametrize("enable_multiple_clients", [True, False])
def test_acquire_session_multiple_clients(
    mock_interactive_session_block, enable_multiple_clients: bool
):
    mock_session = Mock()
    mock_interactive_session_block._ray = Mock()
    mock_interactive_session_block._ray.__version__ = "mock_ray_version"
    mock_interactive_session_block._ray.__commit__ = "mock_ray_commit"
    mock_interactive_session_block._ray.util.connect = Mock(
        side_effect=_connected(mock_interactive_session_block._ray, {"num_clients": 2})
    )

    def disconnected(*a: Any, **kw: Any) -> None:
        mock_interactive_session_block._ray.util.client.ray.is_connected.return_value = (
            False
        )

    # Emulate session lock failure.
    mock_interactive_session_block._ray.util.disconnect.side_effect = disconnected
    mock_interactive_session_block._get_connect_params = Mock(
        return_value=("mock_session_url", "mock_secure", "mock_metadata")
    )
    mock_interactive_session_block._dynamic_check = Mock()

    with patch.multiple(
        "anyscale.connect_utils.start_interactive_session",
        check_required_ray_version=Mock(),
    ):
        mock_interactive_session_block._acquire_session_lock(
            mock_session,
            0,
            True,
            False,
            {},
            job_config=Mock(),
            allow_multiple_clients=enable_multiple_clients,
        )

    assert mock_interactive_session_block._ray.util.connect.call_count == 2
    if enable_multiple_clients:
        # Should be connected successfully if ALLOW_MULTIPLE_CLIENTS = 1
        assert (
            mock_interactive_session_block._ray.util.client.ray.is_connected.return_value
        )
    else:
        # Should not be connected if ALLOW_MULTIPLE_CLIENTS = 0
        assert (
            not mock_interactive_session_block._ray.util.client.ray.is_connected.return_value
        )


@pytest.mark.parametrize(
    "ray_info_resp",
    [
        "",
        json.dumps(
            {"ray_commit": "mock_ray_commit", "ray_version": "mock_ray_version"}
        ).encode(),
    ],
)
def test_acquire_session_lock_failure(
    mock_interactive_session_block, ray_info_resp: str
):
    """
    Test _acquire_session_lock raises error when connection exception.
    """
    mock_interactive_session_block._get_connect_params = Mock(side_effect=RuntimeError)
    mock_interactive_session_block._subprocess = Mock()
    mock_interactive_session_block._subprocess.check_output = Mock(
        return_value=ray_info_resp
    )
    mock_check_required_ray_version = Mock()
    mock_interactive_session_block._ray = Mock()
    mock_interactive_session_block._ray.__version__ = Mock()
    mock_interactive_session_block._ray.__commit__ = Mock()

    mock_session = Mock()
    mock_session.name = "mock_session_name"

    with patch.multiple(
        "anyscale.connect_utils.start_interactive_session",
        check_required_ray_version=mock_check_required_ray_version,
    ):
        with pytest.raises(RuntimeError):
            mock_interactive_session_block._acquire_session_lock(
                mock_session, 0, True, False, {}
            )
    if ray_info_resp:
        mock_check_required_ray_version.assert_called_with(
            mock_interactive_session_block.log,
            mock_interactive_session_block._ray.__version__,
            mock_interactive_session_block._ray.__commit__,
            "mock_ray_version",
            "mock_ray_commit",
            False,
        )


@pytest.mark.parametrize(
    "connect_url",
    [None, "connect-ses-id.anyscale-prod-k8wcxpg-0000.anyscale-test-production.com"],
)
@pytest.mark.parametrize(
    "jupyter_notebook_url",
    [
        None,
        "https://dashboard-ses-id.anyscale-prod-k8wcxpg-0000.anyscale-test-production.com/jupyter/lab?token=mock_access_token",
    ],
)
@pytest.mark.parametrize("secure", [True, False])
def test_get_connect_params(
    mock_interactive_session_block,
    connect_url: Optional[str],
    jupyter_notebook_url: Optional[str],
    secure: bool,
):
    mock_session = Mock()
    mock_session.name = "mock_session_name"
    mock_session.connect_url = connect_url
    mock_session.jupyter_notebook_url = jupyter_notebook_url
    mock_session.access_token = "mock_access_token"

    if not connect_url and not jupyter_notebook_url:
        with pytest.raises(AssertionError):
            mock_interactive_session_block._get_connect_params(mock_session, secure)
        return

    (
        connect_url_output,
        secure_output,
        metadata_output,
    ) = mock_interactive_session_block._get_connect_params(mock_session, secure)

    assert secure_output == secure
    if connect_url:
        assert connect_url_output == connect_url
        assert metadata_output == [("cookie", "anyscale-token=mock_access_token")]
    elif secure:
        assert connect_url_output == (
            jupyter_notebook_url.split("/")[2].lower() if jupyter_notebook_url else None
        )
        assert metadata_output == [
            ("cookie", "anyscale-token=mock_access_token"),
            ("port", "10001"),
        ]
    else:
        assert connect_url_output == (
            jupyter_notebook_url.split("/")[2].lower() + ":8081"
            if jupyter_notebook_url
            else None
        )
        assert metadata_output == [
            ("cookie", "anyscale-token=mock_access_token"),
            ("port", "10001"),
        ]


@pytest.mark.parametrize("python_version", ["3", "2"])
def test_dynamic_check(mock_interactive_session_block, python_version: str):
    mock_interactive_session_block._ray = Mock()
    mock_interactive_session_block._ray.__version__ = "1.8.0"
    mock_interactive_session_block._ray.__commit__ = "mock_commit_id"
    mock_check_required_ray_version = Mock()
    mock_detect_python_minor_version = Mock(return_value="3")
    mock_info = {
        "ray_version": "1.8.0",
        "ray_commit": "mock_commit_id",
        "python_version": python_version,
    }

    with patch.multiple(
        "anyscale.connect_utils.start_interactive_session",
        check_required_ray_version=mock_check_required_ray_version,
        detect_python_minor_version=mock_detect_python_minor_version,
    ):
        if python_version != "3":
            with pytest.raises(AssertionError):
                mock_interactive_session_block._dynamic_check(mock_info, False)
        else:
            mock_interactive_session_block._dynamic_check(mock_info, False)
    mock_check_required_ray_version.assert_called_with(
        mock_interactive_session_block.log,
        mock_interactive_session_block._ray.__version__,
        mock_interactive_session_block._ray.__commit__,
        mock_info["ray_version"],
        mock_info["ray_commit"],
        False,
    )
    mock_detect_python_minor_version.assert_called_with()


@pytest.mark.parametrize("is_connected_resp", [True, False])
@pytest.mark.parametrize(
    "host_name",
    [
        None,
        "https://dashboard-ses-id.anyscale-prod-k8wcxpg-0000.anyscale-test-production.com",
    ],
)
@pytest.mark.parametrize(
    "jupyter_notebook_url",
    [
        None,
        "https://dashboard-ses-id.anyscale-prod-k8wcxpg-0000.anyscale-test-production.com/jupyter/lab?token=mock_access_token",
    ],
)
def test_check_connection(
    mock_interactive_session_block,
    is_connected_resp: bool,
    host_name: Optional[str],
    jupyter_notebook_url: Optional[str],
):
    mock_interactive_session_block._ray = Mock()
    mock_interactive_session_block._ray.util.client.ray.is_connected = Mock(
        return_value=is_connected_resp
    )
    mock_session = Mock(
        id="mock_session_id",
        host_name=host_name,
        jupyter_notebook_url=jupyter_notebook_url,
    )

    if not is_connected_resp:
        with pytest.raises(RuntimeError):
            mock_interactive_session_block._check_connection(mock_session)
    else:
        mock_interactive_session_block._check_connection(mock_session)

    mock_interactive_session_block._ray.util.client.ray.is_connected.assert_called_with()


@pytest.mark.parametrize("initial_scale", [[], [{"mock_key": 1}]])
def test_init(initial_scale: INITIAL_SCALE_TYPE):
    mock_get_interactive_shell_frame = Mock(return_value=None)
    mock_cluster = Mock()
    mock_connection_info = {
        "python_version": "mock_python_version",
        "ray_version": "mock_ray_version",
        "ray_commit": "mock_ray_commit",
        "protocol_version": "mock_protocol_version",
        "num_clients": "mock_num_clients",
    }
    mock_acquire_session_lock = Mock(return_value=mock_connection_info)
    mock_check_connection = Mock()
    mock_ray = Mock()
    mock_ray.__version__ = mock_connection_info["ray_version"]
    mock_ray.__commit__ = mock_connection_info["ray_commit"]
    mock_ray.job_config.JobConfig = Mock
    mock_job_config = Mock()
    mock_log_interactive_session_info = Mock()
    with patch.multiple(
        "anyscale.connect_utils.start_interactive_session",
        get_auth_api_client=Mock(return_value=Mock(),),
        _get_interactive_shell_frame=mock_get_interactive_shell_frame,
    ), patch.multiple(
        "anyscale.connect_utils.start_interactive_session.StartInteractiveSessionBlock",
        _acquire_session_lock=mock_acquire_session_lock,
        _check_connection=mock_check_connection,
        _log_interactive_session_info=mock_log_interactive_session_info,
    ):
        interactive_session_block_output = StartInteractiveSessionBlock(
            mock_cluster,
            mock_job_config,
            False,
            initial_scale,
            False,
            None,
            {},
            True,
            False,
            mock_ray,
            Mock(),
        )

    assert (
        interactive_session_block_output.anyscale_client_context.dashboard_url
        == mock_cluster.ray_dashboard_url
    )
    assert (
        interactive_session_block_output.anyscale_client_context.python_version
        == mock_connection_info["python_version"]
    )
    assert (
        interactive_session_block_output.anyscale_client_context.ray_version
        == mock_connection_info["ray_version"]
    )
    assert (
        interactive_session_block_output.anyscale_client_context.ray_commit
        == mock_connection_info["ray_commit"]
    )
    assert (
        interactive_session_block_output.anyscale_client_context.protocol_version
        == mock_connection_info["protocol_version"]
    )
    assert (
        interactive_session_block_output.anyscale_client_context._num_clients
        == mock_connection_info["num_clients"]
    )
    assert interactive_session_block_output.connection_info == mock_connection_info

    mock_acquire_session_lock.assert_called_with(
        mock_cluster,
        connection_retries=10,
        secure=True,
        ignore_version_check=False,
        ray_init_kwargs={},
        job_config=mock_job_config,
        allow_multiple_clients=False,
    )
    mock_check_connection.assert_called_with(mock_cluster)
    mock_get_interactive_shell_frame.assert_called_with()
    mock_log_interactive_session_info.assert_called_with(
        mock_cluster.id,
        mock_cluster.project_id,
        mock_job_config.metadata.get("job_name"),
    )

    if len(initial_scale):
        mock_ray.autoscaler.sdk.request_resources.assert_called_with(
            bundles=initial_scale
        )

    expected_context = AnyscaleClientContext(
        anyscale_cluster_info=AnyscaleClientConnectResponse(cluster_id="cluster-1"),
        python_version=mock_connection_info["python_version"],
        _num_clients=mock_connection_info["num_clients"],
        ray_version=mock_ray.__version__,
        ray_commit=mock_ray.__commit__,
        protocol_version=mock_connection_info["protocol_version"],
        dashboard_url=mock_cluster.ray_dashboard_url,
    )
    assert interactive_session_block_output.anyscale_client_context == expected_context
