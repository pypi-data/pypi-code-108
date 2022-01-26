from click.testing import CliRunner
from coiled.cli import diagnostics


def test_diagnostics_command(sample_user):
    runner = CliRunner()
    result = runner.invoke(diagnostics.diagnostics)
    if result.exception:
        raise result.exception
    assert result.exit_code == 0
    assert "Performing health check" in result.output
    assert "health_check" in result.output
    assert "Getting user information" in result.output
    assert "user_information" in result.output
