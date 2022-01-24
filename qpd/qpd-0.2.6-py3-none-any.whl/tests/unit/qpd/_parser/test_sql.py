from qpd._parser.sql import QPDSql
from pytest import raises


def test_qpd_sql():
    sql = QPDSql("SELECT * FROM a WHERE x=1", "singleStatement")
    assert "SELECT * FROM a WHERE x=1" == sql.raw_code
    assert "SELECT * FROM a WHERE x=1" == sql.code
    with raises(SyntaxError):
        QPDSql("select * from a where x=1", "singleStatement", ignore_case=False)
    sql = QPDSql("select * from a where x=1", "singleStatement", ignore_case=True)
    assert "select * from a where x=1" == sql.raw_code
    assert "SELECT * FROM a WHERE x=1" == sql.code
