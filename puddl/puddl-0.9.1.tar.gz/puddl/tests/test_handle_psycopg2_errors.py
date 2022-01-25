import pytest
from puddl.pg import DB


def test_foo():
    import psycopg2.errorcodes
    from sqlalchemy.exc import ProgrammingError

    db = DB('psycoerror')

    with pytest.raises(ProgrammingError) as e:
        db.engine.execute('CREATE TABLE foo (x INT)')
        db.engine.execute('CREATE TABLE foo (x INT)')
        assert e.orig.pgcode == psycopg2.errorcodes.DUPLICATE_TABLE
