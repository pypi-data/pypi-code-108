from coiled.cli.core import cli


def test_available_commands():
    assert set(cli.commands) == set(
        ["login", "install", "upload", "env", "create-kubeconfig", "diagnostics"]
    )
