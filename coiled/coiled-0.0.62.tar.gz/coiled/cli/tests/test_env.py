import coiled
import dask
import yaml
from click.testing import CliRunner
from coiled.cli import env


def test_create_list_delete(sample_user):
    # No software environments initially
    assert not coiled.list_software_environments()

    runner = CliRunner()
    name = "my-env"
    # Coiled env create creates a software environment
    result = runner.invoke(
        env.create, args=f"--name {name} --container daskdev/dask:latest"
    )
    assert result.exit_code == 0

    result = coiled.list_software_environments()
    assert f"{sample_user.account.name}/{name}" in result
    assert (
        result[f"{sample_user.account.name}/{name}"]["container"]
        == "daskdev/dask:latest"
    )

    # Coiled env list has similar output to coiled.list_software_environments
    result = runner.invoke(env.list, color=False)
    assert result.exit_code == 0
    output = yaml.safe_load(result.output)
    assert f"{sample_user.account.name}/{name}" in output
    assert (
        output[f"{sample_user.account.name}/{name}"]["container"]
        == "daskdev/dask:latest"
    )

    # Coiled delete removes software environments
    result = runner.invoke(env.delete, args=name)
    assert result.exit_code == 0
    assert not coiled.list_software_environments()


def test_inspect(sample_user, second_user, remote_access_url, sample_user_token):
    # Coiled inspect outputs software spec (even from other user's accounts)

    # Create software environment in sample_user's account
    with dask.config.set(
        {
            "coiled": {
                "user": f"{sample_user.user.username}",
                "token": sample_user_token,
                "server": remote_access_url,
                "account": sample_user.account.name,
                "backend-options": {"region": "us-east-2"},
                "no-minimum-version-check": True,
            }
        }
    ):
        coiled.create_software_environment(
            name="my-env", container="daskdev/dask:latest"
        )

    # Inspect the software environment from second_user's account
    with dask.config.set(
        {
            "coiled": {
                "user": f"{second_user.user.username}",
                "token": f"{second_user.user.auth_token.key}",
                "server": remote_access_url,
                "account": None,
                "backend-options": {"region": "us-east-2"},
                "no-minimum-version-check": True,
            }
        }
    ):
        runner = CliRunner()
        result = runner.invoke(env.inspect, args=f"{sample_user.user.username}/my-env")
    assert result.exit_code == 0
    assert all(i in result.output for i in ["pip", "conda", "container"])
    assert "daskdev/dask:latest" in result.output
