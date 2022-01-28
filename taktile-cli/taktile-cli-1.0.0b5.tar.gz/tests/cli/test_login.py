import json
import os

from click.testing import CliRunner

from tktl import main


def test_login(user_key):
    """Test the CLI."""
    u, k = user_key
    runner = CliRunner()
    result = runner.invoke(main.login, [k])
    assert result.exit_code == 0
    assert result.output == f"Authentication successful for user: {u}\n"

    result = runner.invoke(main.login, ["FAKEAPIKEY"])
    assert result.exit_code == 0
    assert result.output == "Authentication failed: Key format is invalid\n"
    with open(os.path.expanduser("~/.config/tktl/config.json"), "r") as j:
        d = json.load(j)
    assert d["api-key"] != "FAKEAPIKEY"
    assert d["api-key"] == k
