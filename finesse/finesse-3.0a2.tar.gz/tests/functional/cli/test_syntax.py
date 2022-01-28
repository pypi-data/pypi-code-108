"""CLI syntax command tests."""

import pytest
from finesse.__main__ import syntax
from finesse.script.spec import KatSpec
from .util import sanitized_output


@pytest.mark.parametrize("directive", KatSpec().directives)
def test_syntax(cli, directive):
    """Test syntax output."""
    # Search for the specified directive.
    cli_result = cli.invoke(syntax, [directive])
    output = sanitized_output(cli_result)
    assert cli_result.exit_code == 0
    assert directive in output
