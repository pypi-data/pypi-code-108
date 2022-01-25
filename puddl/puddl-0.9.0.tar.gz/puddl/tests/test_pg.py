import pytest

from puddl.exc import DBException
from puddl.pg import DB


def test_create_and_connect():
    db1 = DB('unittest')
    db1.engine.execute('SELECT 1').first()

    db2 = DB('unittest')
    db2.engine.execute('SELECT 1').first()


def test_puddl_access():
    from puddl.conf import DBConfig
    import sqlalchemy
    db = DB('unittest')
    with db.engine.connect() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS test_puddl_access (x INTEGER)')
        conn.execute('DELETE FROM test_puddl_access')
        conn.execute('INSERT INTO test_puddl_access (x) VALUES (23)')
    # puddl may read and modify data
    # stuff should still be owned by the application
    root_db_config = DBConfig()
    root_db_config.PGDATABASE = db.name
    root_engine = sqlalchemy.create_engine(root_db_config.url)
    with root_engine.connect() as conn:
        result = conn.execute('SELECT * FROM test_puddl_access')
        assert result.one()._mapping == {'x': 23}


def test_invalid_name():
    with pytest.raises(DBException):
        DB('`')


def test_df_dump():
    import logging
    logging.getLogger('puddl.db.alchemy').setLevel(logging.DEBUG)
    import pandas as pd
    db = DB('unittest')
    df = pd.DataFrame({'foo': [1, 2], 'bar': [5, 6]})
    db.df_dump(df, 'test_df_dump')
