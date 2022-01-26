import json
from io import StringIO

import yaml
from click.testing import CliRunner

from tktl import main
from tktl.cli import get


def test_get(logged_in_context):
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(main.get_commands)
    assert result.exit_code == 0
    assert "deployments   Get deployment resources\n" in result.output
    assert "repositories  Get repository resources\n" in result.output
    assert "endpoints     Get endpoint resources\n" in result.output


def test_get_deployments(logged_in_context):
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(get.get_deployment_by_repo_id)
    assert result.exit_code == 0, result.output
    assert "427cae9a-275f-469f-acc0-5478614ec863" in result.output
    assert "c3da3eb8-2fce-434b-96f0-6a78a200234b" in result.output

    as_io = StringIO(result.output)
    lines = as_io.readlines()
    assert len(lines) >= 6


def test_get_deployments_with_options(logged_in_context):
    runner = CliRunner()
    result_with_id = runner.invoke(
        get.get_deployment_by_repo_id, "99ffb2dc-b06d-4262-b2e0-34cd40a0c56d"
    )
    assert "refs/heads/master" in result_with_id.output
    assert "e6eec3d" in result_with_id.output
    as_io = StringIO(result_with_id.output)
    lines = as_io.readlines()
    assert len(lines) == 3, lines


def test_json_resources(logged_in_context):
    runner = CliRunner()
    for command in [
        get.get_deployment_by_repo_id,
        get.get_repositories,
        get.get_endpoint_by_deployment_id,
    ]:
        result = runner.invoke(command, ["-O", "json", "-a"])
        assert result.exit_code == 0
        as_io = StringIO(result.output)
        lines = as_io.read()
        loaded = json.loads(lines)
        assert isinstance(loaded, list)
        for item in loaded:
            assert "id" in item.keys() or "deployment_id" in item.keys()


def test_yaml_resources(logged_in_context):
    runner = CliRunner()
    for command in [
        get.get_deployment_by_repo_id,
        get.get_repositories,
        get.get_endpoint_by_deployment_id,
    ]:
        result = runner.invoke(command, ["-O", "yaml", "-a"])
        assert result.exit_code == 0
        as_io = StringIO(result.output)
        lines = as_io.read()
        loaded = [line for line in yaml.safe_load_all(lines)]
        assert len(loaded) >= 3
        assert all([("id" in k.keys() or "deployment_id" in k.keys()) for k in loaded])
