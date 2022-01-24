"""Tests for the CLI."""

from aop2db.utils import get_conn, set_conn
from aop2db.cli import conn, load

from click.testing import CliRunner


class TestCli:
    """Tests for the CLI."""

    def test_load(self):
        """Test the load command."""
        runner = CliRunner()
        result = runner.invoke(load)
        assert result.exit_code == 0

    def test_conn(self):
        """Test the conn command."""
        runner = CliRunner()
        test_conn = "mysql+pymysql://root:my_pass@127.0.0.1:3333/my_db"
        original_conn = get_conn()

        result = runner.invoke(conn, [test_conn])
        assert result.exit_code == 0
        new_conn = get_conn()
        assert new_conn == test_conn

        set_conn(original_conn)
        revert_conn = get_conn()
        assert revert_conn == original_conn
