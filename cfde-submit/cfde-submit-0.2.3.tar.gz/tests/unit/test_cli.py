from click.testing import CliRunner
from cfde_submit.main import cli
from cfde_submit.version import __version__


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert __version__ in result.output
