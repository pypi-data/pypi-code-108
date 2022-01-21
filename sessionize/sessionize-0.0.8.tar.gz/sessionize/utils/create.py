from typing import Optional

import sqlalchemy as sa
from sqlalchemy.schema import DropTable, CreateTable
from sqlalchemy.engine import Engine
from sessionize.utils.type_convert import _type_convert
from sessionize.utils.sa_orm import get_table


def create_table(
    table_name: str,
    column_names: list[str],
    column_types: list[type],
    primary_key: str,
    engine: Engine,
    schema: Optional[str] = None,
    autoincrement: Optional[bool] = True,
    if_exists: Optional[str] = 'error'
) -> sa.Table:
    
    cols = []
    
    for name, python_type in zip(column_names, column_types):
        sa_type = _type_convert[python_type]
        if name == primary_key:
            col = sa.Column(name, sa_type,
                            primary_key=True,
                            autoincrement=autoincrement)
        else:
            col = sa.Column(name, sa_type)
        cols.append(col)

    metadata = sa.MetaData(engine)
    table = sa.Table(table_name, metadata, *cols, schema=schema)
    if if_exists == 'replace':
        drop_table_sql = DropTable(table, if_exists=True)
        engine.execute(drop_table_sql)
    table_creation_sql = CreateTable(table)
    engine.execute(table_creation_sql)
    return get_table(table_name, engine, schema=schema)