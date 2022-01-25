import pandas as pd
from sqlalchemy.types import to_instance, TypeEngine


def to_sql_k(
    df: pd.DataFrame,
    name: str, con, if_exists='fail', index=True,
    index_label=None, schema=None, chunksize=None,
    dtype=None, **kwargs
) -> None:
    """
    Push a Pandas DataFrame to a sql table.
    Similary to DataFrame.to_sql but can add primary key.
    Use keys='key_name' as parameter to add primary key.
    """
    pandas_sql = pd.io.sql.pandasSQL_builder(con, schema=schema)

    if dtype is not None:
        for col, my_type in dtype.items():
            if not isinstance(to_instance(my_type), TypeEngine):
                raise ValueError('The type of %s is not a SQLAlchemy '
                                 'type ' % col)

    table = pd.io.sql.SQLTable(name, pandas_sql, frame=df, index=index,
                               if_exists=if_exists, index_label=index_label,
                               schema=schema, dtype=dtype, **kwargs)
    table.create()
    table.insert(chunksize)