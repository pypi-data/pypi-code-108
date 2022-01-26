from click.testing import CliRunner

from tktl import main


def test_health(logged_in_context, test_user_deployed_repos):
    """Test the CLI."""
    runner = CliRunner()
    for repo, branch, endpoint in test_user_deployed_repos[2:]:
        result = runner.invoke(main.health, ["-r", repo, "-b", branch, "-s", "grpc"])
        assert result.exit_code == 0
        result = runner.invoke(main.health, ["-r", repo, "-b", branch, "-s", "rest"])
        assert result.exit_code == 0


def test_health_fail(test_user_deployed_repos):
    repo, branch, endpoint = test_user_deployed_repos[0]
    runner = CliRunner()
    result = runner.invoke(main.health, ["-r", repo, "-b", branch, "-s", "rest"])
    # User not logged in
    assert result.exit_code == 1


def test_health_local(logged_in_context):
    runner = CliRunner()
    result = runner.invoke(main.health, ["-s", "rest"])
    assert result.exc_info[0] == SystemExit

    result = runner.invoke(main.health, ["-s", "rest", "-l"])
    assert result.exc_info[0] == SystemExit

    # No running local service
    assert result.exit_code == 1
