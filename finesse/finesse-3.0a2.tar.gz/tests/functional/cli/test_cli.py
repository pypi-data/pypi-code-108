"""CLI base group tests."""

from finesse.__main__ import cli as finesse_cli
from .util import sanitized_output


def test_banner(cli):
    """Test printing the banner."""
    cli_result = cli.invoke(finesse_cli, ["--banner"])
    assert "Frequency domain INterferomEter Simulation SoftwarE" in sanitized_output(
        cli_result
    )
    assert cli_result.exit_code == 0
