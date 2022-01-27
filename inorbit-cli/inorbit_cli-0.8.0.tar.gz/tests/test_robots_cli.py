# Copyright (c) 2021, InOrbit, Inc.
# All rights reserved.
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner
from inorbit.cli import apply_config
from inorbit.cli import delete
from inorbit.cli import delete_config
from inorbit.cli import describe_robots
from inorbit.cli import get_config
from inorbit.cli import get_robots
from inorbit.client import InOrbit


@pytest.mark.parametrize(
    "robot_name,response",
    [
        (
            "gont",
            [
                {
                    "id": "121400628",
                    "name": "gont",
                    "agentVersion": "2.3.1",
                    "agentOnline": False,
                    "updatedTs": 1588596807808,
                }
            ],
        )
    ],
)
def test_get_robots(requests_mock, robot_name, response):
    test_client = InOrbit(api_key="foo", url="https://foobar.com")
    # mock CLI client and API
    with mock.patch("inorbit.cli.client", test_client):
        requests_mock.get("https://foobar.com/robots", json=response)

        # call `get_robots`` command and validate output
        runner = CliRunner()
        result = runner.invoke(get_robots)
        assert result.exit_code == 0
        assert robot_name in result.stdout


@pytest.mark.parametrize(
    "robot_name,response",
    [
        (
            "gont",
            [
                {
                    "id": "121400628",
                    "name": "gont",
                    "agentVersion": "2.3.1",
                    "agentOnline": False,
                    "updatedTs": 1588596807808,
                }
            ],
        )
    ],
)
def test_describe_robots(requests_mock, robot_name, response):
    test_client = InOrbit(api_key="foo", url="https://foobar.com")
    # mock CLI client and API
    with mock.patch("inorbit.cli.client", test_client):
        requests_mock.get("https://foobar.com/robots", json=response)

        # call `describe_robots` command and validate output
        runner = CliRunner()
        result = runner.invoke(describe_robots)
        assert result.exit_code == 0
        assert robot_name in result.stdout
        assert "last seen" in result.stdout
        assert "2020-05-04T09:53:27.808000" in result.stdout


def test_apply_config(requests_mock):
    test_client = InOrbit(api_key="foo", url="https://foobar.com")
    test_config_file = Path(__file__).absolute().parent / "sample_config.json"

    with mock.patch("inorbit.cli.client", test_client):
        requests_mock.post("/configuration/apply", text="Configuration applied")
        # call `apply_config` command and validate output
        runner = CliRunner()
        result = runner.invoke(apply_config, ["-f", str(test_config_file)])
        assert result.exit_code == 0
        assert f"Configuration {test_config_file} applied successfully" in result.stdout

    with mock.patch("inorbit.cli.client", test_client):
        requests_mock.post("/configuration/apply", text="Unexpected error", status_code=400)

        runner = CliRunner()
        result = runner.invoke(apply_config, ["-f", str(test_config_file)])
        assert result.exit_code == 1
        assert "Error: (400) Unexpected error" in result.stdout

    # Assert all calls had the correct payload
    for i in range(2):
        assert "kind" in requests_mock.request_history[i].json()
        assert "metadata" in requests_mock.request_history[i].json()
        assert "spec" in requests_mock.request_history[i].json()
        assert "apiVersion" in requests_mock.request_history[i].json()


def test_get_config(requests_mock):
    test_client = InOrbit(api_key="foo", url="https://foobar.com")
    # mock CLI client and API
    with mock.patch("inorbit.cli.client", test_client):
        requests_mock.get(
            "https://foobar.com/configuration/list",
            json={
                "items": [
                    {
                        "id": "cpuLoadPercentage",
                        "kind": "IncidentDefinition",
                        "label": "My CPU incident",
                        "scope": "company",
                        "suppressed": False,
                    }
                ]
            },
        )

        runner = CliRunner()
        # validate `--kind` is required
        result = runner.invoke(get_config)
        assert result.exit_code == 2

        # get config with a valid kind
        result = runner.invoke(get_config, ["--kind", "IncidentDefinition"])
        assert "cpuLoadPercentage" in result.stdout
        assert "IncidentDefinition" in result.stdout
        assert "My CPU incident" in result.stdout
        assert "company" in result.stdout

        assert result.exit_code == 0
        request_data = requests_mock.request_history[0].qs
        # Validate query data was correct
        assert "IncidentDefinition".lower() in request_data.get("kind")
        assert "company".lower() in request_data.get("scope")
        assert "short".lower() in request_data.get("format")

    with mock.patch("inorbit.cli.client", test_client):
        requests_mock.get(
            "https://foobar.com/configuration/list",
            text="Unsupported object kind Foo",
            status_code=400,
        )

        result = runner.invoke(get_config, ["--kind", "Foo"])
        assert result.exit_code == 1

        assert result.exception.args[0] == "(400) Unsupported object kind Foo"


def test_get_config_definition(requests_mock):
    test_client = InOrbit(api_key="foo", url="https://foobar.com")
    # mock CLI client and API
    with mock.patch("inorbit.cli.client", test_client):
        requests_mock.get(
            "https://foobar.com/configuration/list",
            json={
                "items": [
                    {
                        "metadata": {"scope": "company", "id": "cpuLoadPercentage"},
                        "apiVersion": "v0.1",
                        "spec": {
                            "label": "My CPU INC",
                            "statusId": "cpuLoadPercentage",
                            "error": {
                                "autoActions": [],
                                "manualActions": [],
                                "severity": "SEV 0",
                                "notificationChannels": ["app", "slack#alerts-dev"],
                            },
                            "warning": {
                                "autoActions": [],
                                "manualActions": [],
                                "severity": "SEV 2",
                                "notificationChannels": ["app"],
                            },
                        },
                        "kind": "IncidentDefinition",
                    }
                ]
            },
        )

        runner = CliRunner()

        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            result = runner.invoke(
                get_config,
                ["--kind", "IncidentDefinition", "--scope", "company", "--dump", temp_file.name],
            )

            assert result.exit_code == 0
            request_data = requests_mock.request_history[0].qs

            # Validate query data was correct
            assert "IncidentDefinition".lower() in request_data.get("kind")
            assert "company".lower() in request_data.get("scope")
            assert "full".lower() in request_data.get("format")

        # Check id argument is used as query parameter
        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            result = runner.invoke(
                get_config,
                [
                    "--kind",
                    "IncidentDefinition",
                    "--scope",
                    "company",
                    "--dump",
                    temp_file.name,
                    "cpuLoadPercentage",
                ],
            )
            assert "cpuLoadPercentage".lower() in requests_mock.request_history[1].qs.get("id")


def test_delete_config(requests_mock):
    test_client = InOrbit(api_key="foo", url="https://foobar.com")
    # mock CLI client and API
    with mock.patch("inorbit.cli.client", test_client):
        requests_mock.post(
            "https://foobar.com/configuration/clear", json={"operationStatus": "SUCCESS"}
        )

        runner = CliRunner()
        result = runner.invoke(delete_config, ["--kind", "IncidentDefinition", "foo"])
        assert result.exit_code == 0
        request_data = requests_mock.request_history[0].json()
        # Validate query data was correct
        assert request_data.get("kind") == "IncidentDefinition"
        assert request_data.get("apiVersion") == "v0.1"
        assert request_data.get("metadata")
        assert request_data["metadata"].get("id") == "foo"
        assert request_data["metadata"].get("scope") == "company"

        # Validate `--scope` option
        result = runner.invoke(
            delete_config, ["foo", "--kind", "IncidentDefinition", "--scope", "bar"]
        )
        assert result.exit_code == 0
        request_data = requests_mock.request_history[1].json()
        assert request_data["metadata"].get("scope") == "bar"


def test_delete_config_from_file(requests_mock):
    test_client = InOrbit(api_key="foo", url="https://foobar.com")
    test_config_file = Path(__file__).absolute().parent / "sample_config.json"

    # mock CLI client and API
    with mock.patch("inorbit.cli.client", test_client):
        requests_mock.post(
            "https://foobar.com/configuration/clear", json={"operationStatus": "SUCCESS"}
        )

        runner = CliRunner()
        result = runner.invoke(delete)
        assert "Usage: delete [OPTIONS] COMMAND [ARGS]..." in result.output

        result = runner.invoke(delete, ["-f"])
        assert result.exit_code == 2
        assert "Option '-f' requires an argument." in result.output

        result = runner.invoke(delete, ["-f", str(test_config_file)])
        assert result.exit_code == 0
        request_data = requests_mock.request_history[0].json()
        # Validate query data was correct
        assert request_data.get("kind") == "IncidentDefinition"
        assert request_data.get("apiVersion") == "v0.1"
        assert request_data.get("metadata")
        assert request_data["metadata"].get("id") == "cpuLoadPercentage"
        assert request_data["metadata"].get("scope") == "company"
