import json
import os

from tktl.commands.login import LogInCommand, SetApiKeyCommand


def test_set_api_key_command(capsys):
    cmd = SetApiKeyCommand()
    cmd.execute(api_key=None)
    out, err = capsys.readouterr()
    assert "API Key cannot be empty.\n" == err

    cmd.execute(api_key="ABC")
    assert os.path.exists(os.path.expanduser("~/.config/tktl/config.json"))
    with open(os.path.expanduser("~/.config/tktl/config.json"), "r") as j:
        d = json.load(j)
        assert d["api-key"] == "ABC"


def test_login_command(capsys):
    cmd = LogInCommand()
    k = os.environ["TEST_USER_API_KEY"]
    assert cmd.execute(k) is True
    out, err = capsys.readouterr()
    assert out == f"Authentication successful for user: {os.environ['TEST_USER']}\n"
    assert cmd.execute(None) is False


def test_login_fail_command(capfd):
    cmd = LogInCommand()
    assert cmd.execute() is False
    out, err = capfd.readouterr()
    assert err == "Authentication failed: no key provided\n"

    assert cmd.execute(api_key="INVALID_UUID") is False
    out, err = capfd.readouterr()
    assert err == "Authentication failed: Key format is invalid\n"
