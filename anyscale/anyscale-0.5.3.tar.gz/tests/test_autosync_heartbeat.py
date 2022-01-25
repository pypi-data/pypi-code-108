import subprocess
from typing import Any, Dict, List
from unittest.mock import call, Mock, patch

import pytest

from anyscale.authenticate import get_auth_api_client
from anyscale.autosync_heartbeat import (
    managed_autosync_session,
    perform_autopush_synchronization,
)


def test_managed_autosync_session() -> None:
    with patch.multiple(
        "anyscale.authenticate.AuthenticationBlock",
        _validate_api_client_auth=Mock(),
        _validate_credentials_format=Mock(),
    ):
        mock_api_client = get_auth_api_client(
            cli_token="fake_cli_token", host="fake_host"
        ).api_client
    mock_api_client.register_autosync_session_api_v2_autosync_sessions_post = Mock(
        return_value=Mock(result=Mock(id=1))
    )
    mock_api_client.deregister_autosync_session_api_v2_autosync_sessions_autosync_session_id_delete = Mock(
        return_value=None
    )

    with managed_autosync_session("id", mock_api_client):
        pass

    mock_api_client.register_autosync_session_api_v2_autosync_sessions_post.assert_called_once_with(
        "id"
    )
    mock_api_client.deregister_autosync_session_api_v2_autosync_sessions_autosync_session_id_delete.assert_called_once_with(
        1
    )


# Tests autosync without delete flag
def test_perform_autopush_synchronization() -> None:
    mock_proc = Mock()
    mock_proc.stdout = Mock()

    def readline(*args: List[Any], **kwargs: Dict[str, Any]) -> bytes:
        return b"30"

    mock_proc.stdout.readline.side_effect = readline

    class MockTimer:
        def __init__(self, time: int, func: Any):
            self._func = func

        def start(self) -> None:
            self._func()

    with patch("anyscale.autosync_heartbeat.subprocess.Popen") as mock_popen, patch(
        "anyscale.autosync_heartbeat.subprocess.check_output"
    ) as mock_check_output, patch(
        "anyscale.autosync_heartbeat.subprocess.run"
    ) as mock_run, patch(
        "anyscale.autosync_heartbeat.get_rsync_command"
    ) as mock_get_rsync_command, patch(
        "anyscale.autosync_heartbeat.Timer", new=MockTimer
    ), patch(
        "anyscale.autosync_heartbeat.sys.platform", new="darwin"
    ), patch(
        "anyscale.autosync_heartbeat.os.path.dirname"
    ) as mock_dir_name:
        mock_dir_name.return_value = "test"
        mock_popen.return_value.__enter__.return_value = mock_proc
        # Mock no deleted files
        mock_check_output.return_value = b""
        # Raise exception to exit out of infinite loop
        mock_run.side_effect = Exception()
        mock_get_rsync_command.return_value = (["rsync", "test"], {"test-env": "test"})

        with pytest.raises(Exception):
            perform_autopush_synchronization(
                ["ssh"],
                "project_folder",
                "test-user",
                "1.1.1.1",
                "target_folder",
                False,
            )

        mock_popen.assert_called_once_with(
            ["test/fswatch-darwin", "project_folder", "-o"],
            stdout=subprocess.PIPE,
            env={"DYLD_LIBRARY_PATH": "test"},
        )

        mock_get_rsync_command.assert_has_calls(
            [
                call(
                    ["ssh"],
                    "project_folder",
                    "test-user",
                    "1.1.1.1",
                    "target_folder",
                    delete=True,
                    dry_run=True,
                    rsync_exclude=[],
                    rsync_filter=[],
                ),
                call(
                    ["ssh"],
                    "project_folder",
                    "test-user",
                    "1.1.1.1",
                    "target_folder",
                    False,
                    rsync_exclude=[],
                    rsync_filter=[],
                ),
            ]
        )

        mock_run.assert_called_once_with(["rsync", "test"], env={"test-env": "test"})


# Tests autosync with delete flag
def test_perform_autopush_synchronization_with_delete_flag_on() -> None:
    mock_proc = Mock()
    mock_proc.stdout = Mock()

    def readline(*args: List[Any], **kwargs: Dict[str, Any]) -> bytes:
        return b"30"

    mock_proc.stdout.readline.side_effect = readline

    class MockTimer:
        def __init__(self, time: int, func: Any):
            self._func = func

        def start(self) -> None:
            self._func()

    with patch("anyscale.autosync_heartbeat.subprocess.Popen") as mock_popen, patch(
        "anyscale.autosync_heartbeat.subprocess.check_output"
    ) as mock_check_output, patch(
        "anyscale.autosync_heartbeat.subprocess.run"
    ) as mock_run, patch(
        "anyscale.autosync_heartbeat.get_rsync_command"
    ) as mock_get_rsync_command, patch(
        "anyscale.autosync_heartbeat.Timer", new=MockTimer
    ), patch(
        "anyscale.autosync_heartbeat.sys.platform", new="darwin"
    ), patch(
        "anyscale.autosync_heartbeat.os.path.dirname"
    ) as mock_dir_name:
        mock_dir_name.return_value = "test"
        mock_popen.return_value.__enter__.return_value = mock_proc
        # Raise exception to exit out of infinite loop
        mock_run.side_effect = Exception()
        mock_get_rsync_command.return_value = (["rsync", "test"], {"test-env": "test"})

        with pytest.raises(Exception):
            perform_autopush_synchronization(
                ["ssh"],
                "project_folder",
                "test-user",
                "1.1.1.1",
                "target_folder",
                True,
            )

        mock_popen.assert_called_once_with(
            ["test/fswatch-darwin", "project_folder", "-o"],
            stdout=subprocess.PIPE,
            env={"DYLD_LIBRARY_PATH": "test"},
        )

        mock_get_rsync_command.assert_called_once_with(
            ["ssh"],
            "project_folder",
            "test-user",
            "1.1.1.1",
            "target_folder",
            True,
            rsync_exclude=[],
            rsync_filter=[],
        )

        mock_check_output.assert_not_called()

        mock_run.assert_called_once_with(["rsync", "test"], env={"test-env": "test"})


# Tests autosync without delete flag
def test_perform_autopush_synchronization_with_exclude_and_filter() -> None:
    mock_proc = Mock()
    mock_proc.stdout = Mock()

    def readline(*args: List[Any], **kwargs: Dict[str, Any]) -> bytes:
        return b"30"

    mock_proc.stdout.readline.side_effect = readline

    class MockTimer:
        def __init__(self, time: int, func: Any):
            self._func = func

        def start(self) -> None:
            self._func()

    with patch("anyscale.autosync_heartbeat.subprocess.Popen") as mock_popen, patch(
        "anyscale.autosync_heartbeat.subprocess.check_output"
    ) as mock_check_output, patch(
        "anyscale.autosync_heartbeat.subprocess.run"
    ) as mock_run, patch(
        "anyscale.autosync_heartbeat.get_rsync_command"
    ) as mock_get_rsync_command, patch(
        "anyscale.autosync_heartbeat.Timer", new=MockTimer
    ), patch(
        "anyscale.autosync_heartbeat.sys.platform", new="darwin"
    ), patch(
        "anyscale.autosync_heartbeat.os.path.dirname"
    ) as mock_dir_name:
        mock_dir_name.return_value = "test"
        mock_popen.return_value.__enter__.return_value = mock_proc
        # Mock no deleted files
        mock_check_output.return_value = b""
        # Raise exception to exit out of infinite loop
        mock_run.side_effect = Exception()
        mock_get_rsync_command.return_value = (["rsync", "test"], {"test-env": "test"})

        with pytest.raises(Exception):
            perform_autopush_synchronization(
                ["ssh"],
                "project_folder",
                "test-user",
                "1.1.1.1",
                "target_folder",
                False,
                rsync_exclude=["**/.git", "**/.git/**"],
                rsync_filter=[".gitignore"],
            )

        mock_popen.assert_called_once_with(
            ["test/fswatch-darwin", "project_folder", "-o"],
            stdout=subprocess.PIPE,
            env={"DYLD_LIBRARY_PATH": "test"},
        )

        mock_get_rsync_command.assert_has_calls(
            [
                call(
                    ["ssh"],
                    "project_folder",
                    "test-user",
                    "1.1.1.1",
                    "target_folder",
                    delete=True,
                    dry_run=True,
                    rsync_exclude=["**/.git", "**/.git/**"],
                    rsync_filter=[".gitignore"],
                ),
                call(
                    ["ssh"],
                    "project_folder",
                    "test-user",
                    "1.1.1.1",
                    "target_folder",
                    False,
                    rsync_exclude=["**/.git", "**/.git/**"],
                    rsync_filter=[".gitignore"],
                ),
            ]
        )

        mock_run.assert_called_once_with(["rsync", "test"], env={"test-env": "test"})
