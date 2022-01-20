import time
import pandas as pd
from jcutil.drivers import db


def quick_update(schema, target: str, set_cols, where_cols, data, /,
                 mode='update'):
    """利用pandas快速生成的临时表来批量更新数据

    **使用RPLACE模式需要注意，如果传入的数据字段少于原有字段，则原表中的这些字段将被至为NULL**

    Args:
        schema (str): Database bind alias name
        target (str): update target table name
        set_cols (str, list[str]): Will be updated columns. 'id,name,somecol' or ['id','name','somecol']
        where_cols (str, list[str]): Columns that be used in where. 'id,name,somecol' or ['id', 'name', 'somecol']
        data (Iterable, DataFrame): a data that can pass to pd.DataFrame
        mode (str, optional): sql mode: ['update', 'replace']. Defaults to 'update'.
    
    Exceptions:
        ValueError: some column in set_cols or where_cols which is not in target table.
    """
    temp_name = f'tmp_{int(time.time())}'
    if isinstance(where_cols, (str, bytes)):
        where_cols = where_cols.split(',')
    if isinstance(set_cols, (str, bytes)):
        set_cols = set_cols.split(',')
    target_columns = set(pd.read_sql(f'describe {target}', db.conn(schema)).Field.values)
    df = pd.DataFrame(data)
    if diff := (set(set_cols) - target_columns):
        raise ValueError(f'set_cols: {diff} columns not in target table.')
    if diff := (set(where_cols) - target_columns):
        raise ValueError(f'where_cols: {diff} columns not in target table.')
    cols = [col for col in df.columns if col in target_columns]

    if df.empty or not cols:
        return
    if mode == 'update':
        sql = 'UPDATE {target} t, {source} s SET {sets} WHERE {where}'.format(
            target=target,
            source=temp_name,
            sets=','.join([f't.{c} = s.{c}' for c in set_cols]),
            where=' AND '.join([f't.{c} = s.{c}' for c in where_cols]),
        )
    else:
        sql = 'REPLACE INTO {target} ({sets}) SELECT {sets} FROM {source}'.format(
            target=target, source=temp_name,
            sets=','.join(cols)
        )
    with db.conn(schema) as conn:
        conn.execute(f'create table {temp_name} like {target}')
        df[cols].to_sql(temp_name, conn, index=False, if_exists='append')
        conn.execute(sql)
        conn.execute(f'drop table {temp_name}')
