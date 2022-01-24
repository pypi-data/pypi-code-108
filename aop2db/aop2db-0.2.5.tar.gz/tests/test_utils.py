"""Tests for the utils module."""

from aop2db.utils import get_conn, set_conn


class TestImporter:
    """Tests for the utils module."""

    def test_set_conn(self):
        """Test the set_conn method."""
        test_conn = "test_conn_string"
        original_conn = get_conn()

        set_conn(test_conn)
        new_conn = get_conn()
        assert new_conn == test_conn

        set_conn(original_conn)
        revert_conn = get_conn()
        assert revert_conn == original_conn
