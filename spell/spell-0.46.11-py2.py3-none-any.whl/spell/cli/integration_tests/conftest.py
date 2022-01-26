import os
import json
import click.testing
import pytest

from spell.api.user_client import UserClient
from spell.cli.main import cli
from spell.cli.integration_tests.testing_utils import GitFactory
from spell.cli.utils.command import command


def pytest_addoption(parser):
    parser.addoption(
        "--api_url",
        type=str,
        default="http://localhost:5000",
        help="address of the api server to hit",
    )
    parser.addoption("--version_str", type=str, default="v1", help="api version string")


@pytest.fixture(scope="session")
def node_id(request):
    """ID of pytest node that session is running in"""
    return getattr(request.config, "slaveinput", {}).get("slaveid", "")


@pytest.fixture(scope="session")
def api_url(request):
    return request.config.getoption("--api_url")


@pytest.fixture(scope="session")
def version_str(request):
    return request.config.getoption("--version_str")


@pytest.fixture(scope="session")
def spell_dir_perm(tmpdir_factory):
    """pytest fixture that returns a path to the global config file for this session"""
    return spell_dir_helper(tmpdir_factory)


@pytest.fixture(scope="function")
def spell_dir_tmp(tmpdir_factory):
    """pytest fixture that returns a path to a new global config file for this test only"""
    return spell_dir_helper(tmpdir_factory)


def spell_dir_helper(tmpdir_factory):
    """helper method for spell_dir_tmp() and spell_dir_perm()"""
    d = tmpdir_factory.mktemp(".spell")
    d.ensure(dir=True)
    return str(d)


@pytest.fixture(scope="session")
def user_info(api_url, version_str, node_id):
    """pytest fixture that returns a tuple of (spell.api.models.User, password) for the main user for this session"""
    u = UserClient(base_url=api_url, version_str=version_str)
    password = "password"
    user = u.create(
        "cli_test{}".format(node_id),
        "cli_test{}@spell.ml".format(node_id),
        password,
        "unusedRecaptchaToken",
        "MyFirstName MyLastName",
        terms_accepted=True,
    )
    return (user, password)


@pytest.fixture(scope="session")
def ssh_no_host_key_check():
    os.environ["GIT_SSH"] = "ssh -o StrictHostKeyChecking=no"


@pytest.fixture(scope="session")
def login(api_url, version_str, spell_dir_perm, user_info, ssh_no_host_key_check):
    """pytest fixture that runs the `spell login` command once per session"""
    (user, password) = user_info
    runner = click.testing.CliRunner(mix_stderr=False)
    cli_args = [
        "--spell-dir",
        spell_dir_perm,
        "--api-url",
        api_url,
        "--api-version",
        version_str,
    ]

    login_cmd = [
        "login",
        "--identity",
        user.email,
        "--password",
        password,
    ]
    result = runner.invoke(cli, cli_args + login_cmd)
    assert result.exit_code == 0


@pytest.fixture(scope="session")
def run(spell_dir_perm, api_url, version_str, login):
    """
    pytest fixture that returns a function to run spell commands that wraps global arguments for testing
    When runs are executed using this method the state of environment will be already logged in with the
    "session" user
    """
    runner = click.testing.CliRunner(mix_stderr=False)

    def run(args, input=None):
        """given a list of args and optional input, invoke the spell CLI and return a click.testing.Result object"""
        args = [
            "--spell-dir",
            spell_dir_perm,
            "--api-url",
            api_url,
            "--api-version",
            version_str,
        ] + args
        return runner.invoke(cli, args, input=input)

    return run


@pytest.fixture(scope="function")
def run_logged_out(api_url, version_str):
    """
    pytest fixture that returns a function to run spell commands that wraps global arguments for testing
    When runs are executed using this method the state of environment will fresh with no logged in user
    """
    runner = click.testing.CliRunner(mix_stderr=False)

    def run(spell_dir_tmp, args, input=None):
        """given a list of args and optional input, invoke the spell CLI and return a click.testing.Result object"""
        args = [
            "--spell-dir",
            spell_dir_tmp,
            "--api-url",
            api_url,
            "--api-version",
            version_str,
        ] + args
        return runner.invoke(cli, args, input=input)

    return run


@pytest.fixture(scope="session")
def git_factory(tmpdir_factory):
    return GitFactory(tmpdir_factory)


@pytest.fixture(scope="session")
def full_params_cmd():
    @command(name="cmd", short_help="a test func")
    @click.argument("arg1")
    @click.argument("args", nargs=-1)
    @click.option("--flag1", "-f1", is_flag=True)
    @click.option("--multiple", "-m", multiple=True)
    @click.option("--nargs", nargs=2)
    @click.option("--opt", "-o")
    @click.option("--required", "-r", required=True)
    @click.option("--thing/--no-thing")
    @click.option("-v", "--verbose", count=True)
    def cmd(**kwargs):
        click.echo(json.dumps(kwargs))

    return cmd
