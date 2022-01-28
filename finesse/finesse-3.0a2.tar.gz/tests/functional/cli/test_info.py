"""CLI info command tests."""

from finesse.__main__ import info
from .util import sanitized_output


def test_info(cli, input_file):
    """Test info output."""
    cli_result = cli.invoke(info, [input_file])
    assert "Summary:" in sanitized_output(cli_result)
    assert cli_result.exit_code == 0
