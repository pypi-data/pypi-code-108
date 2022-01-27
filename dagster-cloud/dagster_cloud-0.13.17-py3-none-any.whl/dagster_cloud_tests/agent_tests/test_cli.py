# pylint: disable=unused-argument
import os
import tempfile
from pathlib import Path

import mock
from dagster.core.test_utils import environ
from dagster_cloud.agent.cli import app
from typer.testing import CliRunner


def _check_dagster_home(expected: str):
    def _check_inner():
        assert os.getenv("DAGSTER_HOME") == expected

    return _check_inner


def test_run_command_with_env():
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        with environ({"DAGSTER_HOME": temp_dir}):
            with mock.patch(
                "dagster_cloud.agent.cli.run_local_agent", _check_dagster_home(temp_dir)
            ):
                result = runner.invoke(app, [])

                assert result.exit_code == 0, result.output + " : " + str(result.exception)


def test_run_command_with_no_home():
    runner = CliRunner()

    with environ({"DAGSTER_HOME": None}):
        result = runner.invoke(app, [])

        assert result.exit_code == 1, result.output + " : " + str(result.exception)
        assert "No directory provided" in result.output


def test_run_command_with_argument():
    runner = CliRunner()

    # Test param works
    with tempfile.TemporaryDirectory() as temp_dir:
        with mock.patch(
            "dagster_cloud.agent.cli.run_local_agent",
            _check_dagster_home(str(Path(temp_dir).resolve())),
        ):
            result = runner.invoke(app, [temp_dir])

            assert result.exit_code == 0, result.output + " : " + str(result.exception)

    # Test param overrides DAGSTER_HOME env var
    with tempfile.TemporaryDirectory() as temp_dir, tempfile.TemporaryDirectory() as temp_dir_env:
        with environ({"DAGSTER_HOME": temp_dir_env}):
            with mock.patch(
                "dagster_cloud.agent.cli.run_local_agent",
                _check_dagster_home(str(Path(temp_dir).resolve())),
            ):
                result = runner.invoke(app, [temp_dir])

                assert result.exit_code == 0, result.output + " : " + str(result.exception)
