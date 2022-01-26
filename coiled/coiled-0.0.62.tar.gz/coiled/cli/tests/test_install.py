import shutil
from uuid import uuid4

import pytest
from click.testing import CliRunner
from coiled.cli.install import DEFAULT_PIP_PACKAGES, install, remote_name_to_local_name
from coiled.cli.utils import conda_command, parse_conda_command

from cloud.models import SoftwareEnvironment, SoftwareEnvironmentBuild
from software_environments.type_defs import BuildType, CondaSpec

pytestmark = pytest.mark.skipif(
    shutil.which("conda") is None,
    reason="Conda is needed to create local software environments",
)


@pytest.fixture
def senv_with_no_builds(sample_user):
    name = str(uuid4())
    conda_spec = CondaSpec(channels=["conda-forge"], dependencies=["backoff=1.6.0"])

    senv = SoftwareEnvironment.objects.create(
        container="dask/dask",
        conda=conda_spec,
        pip=["toolz"],
        conda_env_name="not-base",
        post_build=["export FOO=BARBAZ", "echo $FOO"],
        content_hash="blah",
        identifier=name,
        name=name,
        account=sample_user.account,
        private=True,
        creator=sample_user.user,
        environment_variables={"MY_TESTING_ENV": "VAR"},
    )
    return senv


def test_install_bad_name_raises(sample_user):
    bad_name = "not-a-software-environment"
    runner = CliRunner()
    result = runner.invoke(install, [bad_name])

    assert result.exit_code != 0
    err_msg = str(result.exception).lower()
    assert "could not find" in err_msg
    assert bad_name in err_msg


@pytest.mark.timeout(600)
@pytest.mark.test_group("test_install_bad_solve_raises_informative_message")
def test_install_bad_solve_raises_informative_message(
    sample_user, monkeypatch, senv_with_no_builds
):
    SoftwareEnvironmentBuild.objects.create(
        type=BuildType.CONDA,
        software_environment=senv_with_no_builds,
        conda_from_history={"like": "super", "fake": "oh my gosh"},
        creator=sample_user.user,
        account=sample_user.account,
        active=True,
    )
    runner = CliRunner()
    result = runner.invoke(install, [senv_with_no_builds.name])

    assert result.exit_code != 0
    keywords = [
        "solved conda environment",
        senv_with_no_builds.name,
        "conda-forge",
        "backoff",
    ]
    for keyword in keywords:
        assert keyword in str(result.exception)


@pytest.mark.timeout(600)
@pytest.mark.test_group("test_install_conda")
def test_install_core(sample_user, senv_with_no_builds):
    SoftwareEnvironmentBuild.objects.create(
        type=BuildType.CONDA,
        software_environment=senv_with_no_builds,
        conda_solved_linux={
            "channels": ["conda-forge"],
            "dependencies": ["backoff=1.6.0"],
        },
        conda_solved_osx={
            "channels": ["conda-forge"],
            "dependencies": ["backoff=1.6.0"],
        },
        conda_solved_windows=None,
        conda_from_history={"like": "super", "fake": "oh my gosh"},
        creator=sample_user.user,
        account=sample_user.account,
        active=True,
    )

    runner = CliRunner()
    result = runner.invoke(install, [senv_with_no_builds.name])

    assert result.exit_code == 0
    output = result.output.lower()
    assert "conda activate" in output
    assert senv_with_no_builds.name in output
    local_name = remote_name_to_local_name(
        account=sample_user.user.username, name=senv_with_no_builds.name
    )
    # switched from pip to json as in failure states
    # using pip commands defaults to the system pip
    # yielding false passing tests
    cmd = [conda_command(), "list", "-n", local_name, "--json"]
    output = parse_conda_command(cmd)
    for package in [*DEFAULT_PIP_PACKAGES, "backoff", "toolz"]:
        assert any(i["name"] == package for i in output)

    assert "BARBAZ" in result.output
    output = parse_conda_command(cmd)
