import asyncio
import io
import sys
from unittest.mock import AsyncMock

import aiobotocore
import coiled
import pytest
import yaml
from coiled.errors import ServerError
from dask.distributed import Client
from distributed.utils_test import loop  # noqa: F401

from common.exceptions import SoftwareEnvironmentBuildError

# fixtures
from software_environments.tests.conftest import aws_module  # noqa: F401
from software_environments.tests.conftest import conda_spec  # noqa: F401
from software_environments.tests.conftest import create_repository_mock  # noqa: F401
from software_environments.tests.conftest import describe_repository_mock  # noqa: F401
from software_environments.tests.conftest import get_ecr_auth_mock  # noqa: F401
from software_environments.tests.conftest import mock_aws  # noqa: F401
from software_environments.tests.conftest import mock_conda_helpers  # noqa: F401
from software_environments.tests.conftest import mock_docker  # noqa: F401
from software_environments.tests.conftest import parse_ecr_uri_mock  # noqa: F401


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_update_software_environment_conda(cloud, cleanup, sample_user, tmp_path):
    # below is what yaml.load(<env-file>) gives
    out = io.StringIO()
    conda_env = {
        "channels": ["defaults"],
        "dependencies": ["python=3.8"],
    }

    await cloud.create_software_environment(name="env-1", conda=conda_env)
    await cloud.create_software_environment(
        name="env-1",
        conda=conda_env,
        log_output=out,
    )

    out.seek(0)
    output = out.read().strip()
    # in process backend has no comparison on hash so will always just rebuild
    assert "Found built image for" or "Building image locally" in output

    conda_env = {
        "channels": ["defaults"],
        "dependencies": ["python=3.8", "toolz"],
    }

    await cloud.create_software_environment(
        name="env-1",
        conda=conda_env,
    )
    senv = coiled.list_software_environments()
    assert len(senv) == 1
    assert "env-1" in str(senv)
    assert "toolz" in str(senv)


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_client_python_version_included_in_conda_deps_for_pip_only_env(
    cloud, cleanup, sample_user, tmp_path
):
    await cloud.create_software_environment(name="env-1", pip=["botocore"])

    senv = coiled.list_software_environments()
    assert len(senv) == 1
    v = ".".join(map(str, sys.version_info[:2]))
    assert f"python={v}" in str(senv)


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_update_software_environment_failure_doesnt_change_db(
    cloud, cleanup, sample_user, mock_docker: AsyncMock
):
    mock_docker.build_and_push.side_effect = ValueError("oh no")
    before_envs = await cloud.list_software_environments()
    out = io.StringIO()
    conda_env = {
        "channels": ["defaults"],
        "dependencies": [
            "dask",
            "not-a-package",
            "pandas",
        ],
    }
    with pytest.raises(Exception):
        await cloud.create_software_environment(
            name="env-1",
            conda=conda_env,
            log_output=out,
        )
    out.seek(0)
    text = out.read()
    assert "oh no" in text.lower()
    after_envs = await cloud.list_software_environments()
    assert before_envs == after_envs


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_software_environment_pip(cloud, cleanup, sample_user, tmp_path):
    packages = ["toolz", "dask"]
    # Provide a list of packages
    await cloud.create_software_environment(name="env-1", pip=packages)

    while True:
        result = await cloud.list_software_environments()
        if result:
            break
        await asyncio.sleep(0.5)

    # Check output is formatted properly
    assert len(result) == 1
    env = result[f"{sample_user.account.name}/env-1"]
    assert env["account"] == sample_user.user.username
    assert env["container"] is None
    assert env["conda"] is not None
    assert env["pip"] == sorted(packages)

    # Provide a local requirements file
    requirements_file = tmp_path / "requirements.txt"
    with requirements_file.open(mode="w") as f:
        f.write("\n".join(packages))

    await cloud.create_software_environment(name="env-2", pip=requirements_file)

    while True:
        result = await cloud.list_software_environments()
        if len(result) == 2:
            break
        await asyncio.sleep(0.5)

    # Check output is formatted properly
    assert len(result) == 2
    env = result[f"{sample_user.account.name}/env-2"]
    assert env["account"] == sample_user.user.username
    assert env["container"] is None
    assert env["conda"] is not None
    assert env["pip"] == sorted(packages)


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_software_environment_pip_private(cloud, cleanup, sample_user):
    packages = ["dask==2.15", "git+https://GIT_TOKEN@github.com/coiled/cloud.git"]
    # Provide a list of packages
    out = io.StringIO()
    with pytest.raises(Exception):
        await cloud.create_software_environment(
            name="env-1", pip=packages, log_output=out
        )
    out.seek(0)
    text = out.read()
    assert "please set up your access token and try again" in text.lower()


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_software_environment_container(cloud, cleanup, sample_user):

    # Provide docker image URI
    await cloud.create_software_environment(
        name="env-1",
        container="daskdev/dask:latest",
    )

    result = await cloud.list_software_environments()

    assert f"{sample_user.account.name}/env-1" in result
    assert "daskdev/dask:latest" in str(result)
    assert "container" in str(result)
    assert sample_user.user.username in str(result)


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_software_environment_multiple_specifications(
    cloud, cleanup, sample_user, tmp_path
):
    container = "continuumio/miniconda:latest"
    conda = {
        "channels": ["defaults"],
        "dependencies": ["python=3.8", {"pip": ["toolz"]}],
    }
    pip = ["requests"]

    # Provide a data structure
    env_name = f"{sample_user.account.name}/env-1"
    await cloud.create_software_environment(
        name=env_name,
        container=container,
        conda=conda,
        pip=pip,
    )

    while True:
        result = await cloud.list_software_environments()
        if result:
            break
        await asyncio.sleep(0.5)

    assert result[env_name]["container"] == container
    assert "python=3.8" in result[env_name]["conda"]["dependencies"]
    assert "toolz" in result[env_name]["pip"]
    assert "requests" in result[env_name]["pip"]

    # Provide local environment / requirements files
    environment_file = tmp_path / "environment.yml"
    with environment_file.open(mode="w") as f:
        f.writelines(yaml.dump(conda))

    requirements_file = tmp_path / "requirements.txt"
    with requirements_file.open(mode="w") as f:
        f.write("\n".join(pip))

    env_name = f"{sample_user.account.name}/env-2"
    await cloud.create_software_environment(
        name=env_name,
        container=container,
        conda=environment_file,
        pip=requirements_file,
    )

    while True:
        result = await cloud.list_software_environments()
        if len(result) == 2:
            break
        await asyncio.sleep(0.5)

    assert result[env_name]["container"] == container
    assert "python=3.8" in result[env_name]["conda"]["dependencies"]
    assert "toolz" in result[env_name]["pip"]
    assert "requests" in result[env_name]["pip"]


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_software_environment_post_build(cloud, cleanup, sample_user, tmp_path):

    container = "daskdev/dask:latest"
    post_build = ["export FOO=BAR--BAZ", "echo $FOO"]
    await cloud.create_software_environment(
        name="env-1",
        container=container,
        post_build=post_build,
    )

    while True:
        results = await cloud.list_software_environments()
        if results:
            break
        print("WARNING: create_software_environment returned early")
        await asyncio.sleep(0.5)

    assert results[f"{sample_user.account.name}/env-1"]["post_build"] == post_build

    post_build_file = tmp_path / "postbuild"
    with post_build_file.open(mode="w") as f:
        f.write("\n".join(post_build))

    await cloud.create_software_environment(
        name="env-2",
        container=container,
        post_build=post_build_file,
    )

    while True:
        results = await cloud.list_software_environments()
        if len(results) == 2:
            break
        print("WARNING: create_software_environment returned early")
        await asyncio.sleep(0.5)

    assert results[f"{sample_user.account.name}/env-2"]["post_build"] == post_build


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_software_environment_build_free_tier_disable(
    disabled_free_tier_cloud, disabled_free_tier_user
):
    container = "daskdev/dask:latest"
    post_build = ["export FOO=BAR--BAZ", "echo $FOO"]

    with pytest.raises(coiled.errors.ServerError):
        await disabled_free_tier_cloud.create_software_environment(
            name="env-1",
            container=container,
            post_build=post_build,
        )


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_delete_software_environment(cloud, cleanup, sample_user):
    # Initially no software environments
    result = await cloud.list_software_environments()
    assert not result

    packages = ["toolz"]

    # Create two configurations
    await cloud.create_software_environment(name="env-1", pip=packages)
    await cloud.create_software_environment(name="env-2", pip=packages)

    while True:
        result = await cloud.list_software_environments()
        print("WARNING: create_software_environment returned early")
        if len(result) == 2:
            break
        await asyncio.sleep(0.5)

    assert len(result) == 2

    # Delete one of the configurations
    await cloud.delete_software_environment(name="env-1")
    result = await cloud.list_software_environments()
    assert len(result) == 1
    assert f"{sample_user.account.name}/env-2" in result


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_conda_raises(cloud, cleanup, sample_user, mock_conda_helpers):
    conda_env = {
        "channels": ["defaults"],
        "dependencies": ["dask", "not-a-package", "pandas", "nomkl"],
    }
    mock_conda_helpers.solve_conda_spec.side_effect = SoftwareEnvironmentBuildError(
        "ResolvePackageNotFound not-a-package"
    )
    out = io.StringIO()
    with pytest.raises(
        ServerError,
        match="ResolvePackageNotFound",
    ):
        await cloud.create_software_environment(
            name="env-1",
            conda=conda_env,
            log_output=out,
        )
    out.seek(0)
    text = out.read()
    assert "not-a-package" in text.lower()


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_conda_uses_name(cloud, sample_user, cleanup):
    conda_env = {
        "name": "my-env",
        "channels": ["defaults"],
        "dependencies": ["python=3.8", "toolz"],
    }

    await cloud.create_software_environment(conda=conda_env)
    while True:
        result = await cloud.list_software_environments()
        if result:
            break
        await asyncio.sleep(0.5)

    assert len(result) == 1
    env = result[f"{sample_user.account.name}/my-env"]
    env_name = env["conda"]["name"]
    assert env_name == "my-env"


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_no_name_raises(cloud, cleanup):
    conda_env = {
        "channels": ["conda-forge"],
        "dependencies": ["toolz"],
    }

    with pytest.raises(ValueError, match="provide a name"):
        await cloud.create_software_environment(conda=conda_env)


@pytest.mark.skip("Simply too slow to run regularly")
@pytest.mark.test_group("veryslow")
@pytest.mark.asyncio
async def test_conda_env_name(cloud, cleanup, backend):
    # Ensure that specifying conda_env_name works as expected
    # Regression test for https://github.com/coiled/cloud/issues/779

    conda_env = {
        "name": "foobar",
        "channels": ["conda-forge"],
        "dependencies": ["toolz", "dask>=2.25.0"],
    }

    await cloud.create_software_environment(
        name="test-conda-env-name",
        container="coiled/test-conda-env-name:latest",
        conda=conda_env,
        conda_env_name="foo",
    )
    while True:
        result = await cloud.list_software_environments()
        if result:
            break
        await asyncio.sleep(5)

    await cloud.create_cluster_configuration(
        name="test-conda-env-name", software="test-conda-env-name"
    )
    async with coiled.Cluster(
        asynchronous=True, configuration="test-conda-env-name"
    ) as cluster:
        async with Client(cluster, asynchronous=True) as client:

            def test_import():
                try:
                    import toolz  # noqa: F401

                    return True
                except ImportError:
                    return False

            result = await client.run_on_scheduler(test_import)
            assert result


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_docker_build_reports_failure(
    cloud, cleanup, sample_user, mock_docker: AsyncMock
):
    """Sometime the docker build can fail, even if the conda solve works"""
    before_envs = await cloud.list_software_environments()
    mock_docker.build_and_push.side_effect = ValueError("Docker build failed 232")
    out = io.StringIO()
    with pytest.raises(ServerError, match="Docker build failed 232") as e:
        await cloud.create_software_environment(
            name="env-1",
            conda=["sqlite"],
            post_build=["exit 1000"],
            log_output=out,
        )
    out.seek(0)
    text = out.read()
    assert "232" in e.value.args[0]  # script throws 232 as the exit code
    assert "failed" in text.lower()

    after_envs = await cloud.list_software_environments()
    assert before_envs == after_envs


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_update_software_environment_privacy(
    cloud,
    cleanup,
    sample_user,
    tmp_path,
):
    await cloud.create_software_environment(
        name="env-1", container="daskdev/dask:latest"
    )

    result = await cloud.list_software_environments()
    env_name = f"{sample_user.account.name}/env-1"
    assert env_name in result
    assert result[env_name]["private"] is False

    await cloud.create_software_environment(
        name="env-1",
        container="daskdev/dask:latest",
        private=True,
    )
    result = await cloud.list_software_environments()

    assert env_name in result
    assert result[env_name]["private"] is True


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_create_software_environment_another_account_fails(
    cloud, cleanup, sample_user, second_user, sample_user_token
):
    # Ensure sample_user is authenticated
    assert cloud.user == sample_user.user.username
    assert cloud.token == sample_user_token

    # Make sure sample_user can't create a software environment
    # in an account they don't belong to
    assert second_user.account.name not in cloud.accounts
    with pytest.raises(ValueError) as excinfo:
        await cloud.create_software_environment(
            name=f"{second_user.account.name}/test-ev", container="daskdev/dask:latest"
        )

    err_msg = str(excinfo.value)
    assert "permissions" in err_msg
    assert second_user.account.name in err_msg


@pytest.mark.django_db(transaction=True)
def test_software_env_coiled_credits(sample_user):
    program = sample_user.account.active_program
    program.update_usage(program.quota + 1)

    with pytest.raises(Exception) as e:
        coiled.create_software_environment(
            name="new-env", container="daskdev/dask:latest"
        )
    assert "You have reached your quota" in e.value.args[0]


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_software_environment_env_variables(
    cloud, cleanup, sample_user, tmp_path
):
    conda_env = {
        "channels": ["defaults"],
        "dependencies": ["python=3.8", {"pip": ["toolz"]}],
    }
    environ = {"MY_TESTING_ENV": "VAL"}

    await cloud.create_software_environment(
        name="env-var", conda=conda_env, environ=environ
    )

    while True:
        result = await cloud.list_software_environments()
        if result:
            break
        await asyncio.sleep(0.5)

    # Check output is formatted properly
    assert len(result) == 1
    env = result[f"{sample_user.account.name}/env-var"]
    assert env["account"] == sample_user.user.username
    assert env["container"] is None
    assert "python=3.8" in env["conda"]["dependencies"]
    assert "toolz" in env["pip"]
    assert env["environ"] == environ
    await cloud.delete_software_environment("env-var")


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
@pytest.mark.parametrize(
    "name",
    [
        "My-Test-Env",
        "My Test Env",
        "my-test-env!",
        "coiled/My-Test-Env",
        "coiled/My-Test-Env:abc123",
        "Coiled/my-test-env",
    ],
)
async def test_software_environment_slug(cloud, cleanup, sample_user, tmp_path, name):
    with pytest.raises(ValueError) as e:
        await cloud.create_software_environment(
            name=name,
            container="daskdev/dask:latest",
        )
    assert "can only contain lowercase ASCII letters" in e.value.args[0]


@pytest.mark.asyncio
@pytest.mark.test_group("software-env-slow-group")
async def test_cant_use_base_container_from_our_private_ecr(
    cloud, cleanup, sample_user, tmp_path
):
    session = aiobotocore.get_session()
    async with session.create_client("sts") as sts:
        account_id = (await sts.get_caller_identity())["Account"]
    container = f"{account_id}.dkr.ecr.us-east-2.amazonaws.com/prod/cloud"
    with pytest.raises(ServerError) as e:
        await cloud.create_software_environment(
            name="steal_some_stuff",
            container=container,
        )
    assert (
        e.value.args[0]
        == 'Access to the base image specified in "container=" is forbidden.'
    )
