from unittest.mock import Mock, patch

import pytest

from anyscale.client.openapi_client.models.execute_command_response import (
    ExecuteCommandResponse,
)
from anyscale.client.openapi_client.models.execute_interactive_command_options import (
    ExecuteInteractiveCommandOptions,
)
from anyscale.client.openapi_client.models.executecommandresponse_response import (
    ExecutecommandresponseResponse,
)
from anyscale.controllers.exec_controller import ExecController


@pytest.fixture()
def mock_api_client(command_id_test_data: ExecuteCommandResponse) -> Mock:
    mock_api_client = Mock()

    mock_api_client.execute_interactive_command_api_v2_sessions_session_id_execute_interactive_command_post = Mock(
        return_value=ExecutecommandresponseResponse(result=command_id_test_data)
    )

    return mock_api_client


@pytest.fixture()
def mock_auth_api_client(mock_api_client: Mock, base_mock_anyscale_api_client: Mock):
    mock_auth_api_client = Mock(
        api_client=mock_api_client, anyscale_api_client=base_mock_anyscale_api_client,
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=Mock(return_value=mock_auth_api_client),
    ):
        yield


def test_anyscale_exec(
    mock_auth_api_client, command_id_test_data: ExecuteCommandResponse
) -> None:
    mock_cluster_config = {"provider": {"default": "value"}, "cluster_name": "cname"}
    mock_get_cluster_config = Mock(return_value=mock_cluster_config)
    mock_rsync = Mock(return_value=None)
    mock_check_call = Mock(return_value=None)
    mock_log = Mock()
    mock_log.format_api_exception.return_value.__enter__ = Mock()
    mock_log.format_api_exception.return_value.__exit__ = Mock()

    exec_controller = ExecController()

    with patch.multiple(
        "anyscale.controllers.exec_controller",
        get_cluster_config=mock_get_cluster_config,
        rsync=mock_rsync,
    ), patch.multiple("subprocess", check_call=mock_check_call):
        commands = ["cmd1", "cmd2"]
        exec_controller._get_session_name_and_id = Mock(  # type: ignore
            return_value=("session_name", "session_id")
        )
        exec_controller._generate_remote_command = Mock(return_value="remote_command")  # type: ignore
        exec_controller.log = mock_log
        exec_controller.anyscale_exec(
            "session_name", True, False, (1000,), True, True, False, commands
        )

    exec_controller.api_client.execute_interactive_command_api_v2_sessions_session_id_execute_interactive_command_post.assert_called_once_with(
        session_id="session_id",
        execute_interactive_command_options=ExecuteInteractiveCommandOptions(
            shell_command=" ".join(commands)
        ),
    )
    exec_controller._get_session_name_and_id.assert_called_once_with("session_name")
    exec_controller._generate_remote_command.assert_called_once_with(
        command_id_test_data.command_id,
        commands,
        command_id_test_data.directory_name,
        True,
        False,
    )
    mock_get_cluster_config.assert_called_once_with(
        "session_name", exec_controller.api_client
    )
    mock_rsync.assert_called_once()
    mock_check_call.assert_called_once()
    exec_controller.log.info.assert_called_once()
