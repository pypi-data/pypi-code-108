import pandas as pd
from jcutil.core import async_run
from jcutil.drivers import db


async def read_sql(schema, sql, **kwargs):
  with db.get_client(schema) as engine:
    return await async_run(pd.read_sql, sql, engine, **kwargs)


async def read_table(schema, table_name, **kwargs):
  with db.get_client(schema) as engine:
    return await async_run(pd.read_sql_table, table_name, engine, **kwargs)


async def counts(schema, table_name, where='') -> int:
  pass
