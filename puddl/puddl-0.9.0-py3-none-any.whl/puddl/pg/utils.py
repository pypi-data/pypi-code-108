import sqlalchemy

from puddl.typing import URL


def list_databases(url: URL):
    engine = sqlalchemy.create_engine(url)
    return [row[0] for row in engine.execute('SELECT name FROM puddl_databases').fetchall()]


def list_schemas(url: URL):
    engine = sqlalchemy.create_engine(url)
    inspection_result = sqlalchemy.inspect(engine)
    return inspection_result.get_schema_names()
