from click.testing import CliRunner
from cfde_submit.main import cli
import fair_research_login.exc


def test_login(mock_login, logged_out):
    runner = CliRunner()
    runner.invoke(cli, ['login'])
    # TODO: Fix token error so this exits with 0
    # result = runner.invoke(cli, ['login'])
    # assert result.exit_code == 0
    assert mock_login.login.called


def test_login_when_logged_in(mock_login, logged_in):
    runner = CliRunner()
    result = runner.invoke(cli, ['login'])
    assert result.exit_code == 0
    assert not mock_login.login.called


def test_logout(mock_login, logged_in):
    runner = CliRunner()
    result = runner.invoke(cli, ['logout'])
    assert result.exit_code == 0
    assert mock_login.logout.called


def test_logout_when_logged_out(mock_login, logged_out):
    runner = CliRunner()
    result = runner.invoke(cli, ['logout'])
    assert result.exit_code == 0
    assert not mock_login.logout.called


def test_login_user_consent_failure(mock_login, logged_out):
    mock_login.login.side_effect = fair_research_login.exc.AuthFailure('Consent Denied')
    runner = CliRunner()
    result = runner.invoke(cli, ['login'])
    assert result.exit_code == 1
    assert mock_login.login.called
    assert 'Consent Denied' in result.stdout
