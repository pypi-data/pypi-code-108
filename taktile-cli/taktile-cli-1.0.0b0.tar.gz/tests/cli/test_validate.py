from click.testing import CliRunner

from tktl import main
from tktl.cli import validate


def test_validate():
    """Test the validation cli."""
    runner = CliRunner()
    result = runner.invoke(main.validate)
    assert result.exit_code == 0
    assert "help" in result.output
    assert "config" in result.output
    assert "all" in result.output
    assert "import" in result.output
    assert "unittest" in result.output
    assert "integration" in result.output
    assert "profiling" in result.output


def test_validate_config():
    """Test the validation cli."""
    runner = CliRunner()
    result = runner.invoke(validate.validate_config_command, ["."])
    assert result.exit_code == 2


def test_validate_all():
    """Test the validation cli."""
    runner = CliRunner()
    result = runner.invoke(validate.validate_all_command, ["."])
    assert result.exit_code == 2


def test_validate_import():
    """Test the validation cli."""
    runner = CliRunner()
    result = runner.invoke(validate.validate_import_command, ["."])
    assert result.exit_code == 2


def test_validate_unittest():
    """Test the validation cli."""
    runner = CliRunner()
    result = runner.invoke(validate.validate_unittest_command, ["."])
    assert result.exit_code == 2


def test_validate_integration():
    """Test the validation cli."""
    runner = CliRunner()
    result = runner.invoke(validate.validate_integration_command, ["."])
    assert result.exit_code == 2


def test_validate_profiling():
    """Test the validation cli."""
    runner = CliRunner()
    result = runner.invoke(validate.validate_profiling_command, ["."])
    assert result.exit_code == 2
