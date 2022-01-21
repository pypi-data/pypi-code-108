
from typing import Optional, Any, Union, Generator

import sqlalchemy as sa
from sqlalchemy.sql import select
from sqlalchemy.sql.elements import and_, or_
from sqlalchemy.exc import PendingRollbackError

from sessionize.utils.sa_orm import get_column, _get_table, get_row_count, primary_keys
from sessionize.utils.custom_types import Record, SqlConnection
from sessionize.exceptions import MissingPrimaryKey, SliceError


def select_records(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    chunksize: Optional[int] = None,
    schema: Optional[str] = None,
    sorted: bool = False,
    include_columns: Optional[list[str]] = None
) -> Union[list[Record], Generator[list[Record], None, None]]:
    """
    Queries database for records in table.
    Returns list of records in sql table.
    Returns a generator of lists of records if chunksize is not None.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    chunksize: int, default None
        if not None, returns generator of lists of records.
    
    Returns
    -------
    list of sql table records or generator of lists of records.
    """
    try:
        table = _get_table(table, connection, schema=schema)
        if chunksize is None:
            return select_records_all(table, connection, sorted=sorted, include_columns=include_columns)
        else:
            return select_records_chunks(table, connection, chunksize, sorted=sorted, include_columns=include_columns)
    except PendingRollbackError:
        connection.rollback()
        return select_records(table, connection, chunksize, schema, sorted, include_columns)




def select_records_all(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    schema: Optional[str] = None,
    sorted: bool = False,
    include_columns: Optional[list[str]] = None
) -> list[Record]:
    """
    Queries database for records in table.
    Returns list of records in sql table.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    
    Returns
    -------
    list of sql table records.
    """
    try:
        table = _get_table(table, connection, schema=schema)
        
        if include_columns is not None:
            columns = [get_column(table, column_name) for column_name in include_columns]
            query = select(*columns)
        else:
            query = select(table)

        if sorted:
            query = query.order_by(*table.primary_key.columns.values())
        results = connection.execute(query)
        return [dict(r) for r in results]
    except PendingRollbackError:
        connection.rollback()
        return select_records_all(table, connection, schema, sorted, include_columns)

def select_records_chunks(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    chunksize: int = 2,
    schema: Optional[str] = None,
    sorted: bool = False,
    include_columns: Optional[list[str]] = None
) -> Generator[list[Record], None, None]:
    """
    Queries database for records in table.
    Returns a generator of chunksized lists of sql table records.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    chunksize: int
        size of lists of sql records generated.
    
    Returns
    -------
    Generator of lists of sql table records.
    """
    try:
        table = _get_table(table, connection, schema=schema)

        if include_columns is not None:
            columns = [get_column(table, column_name) for column_name in include_columns]
            query = select(*columns)
        else:
            query = select(table)

        if sorted:
            query = query.order_by(*table.primary_key.columns.values())
        stream = connection.execute(query, execution_options={'stream_results': True})
        for results in stream.partitions(chunksize):
            yield [dict(r) for r in results]
    except PendingRollbackError:
        connection.rollback()
        return select_records_chunks(table, connection, chunksize, schema, sorted, include_columns)


def select_existing_values(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    column_name: str,
    values: list,
    schema: Optional[str] = None
) -> list:
    """
    Queries database for existing values in table column.
    Returns list of matching values that exist in table column.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    records: list[Record]
        list of records to select from.
        Use df.to_dict('records') to convert Pandas DataFrame to records.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database
    
    Returns
    -------
    List of matching values.
    """
    table = _get_table(table, connection, schema=schema)
    column = get_column(table, column_name)
    query = select([column]).where(column.in_(values))
    return connection.execute(query).scalars().fetchall()


def select_column_values(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    column_name: str,
    chunksize: Optional[int] = None,
    schema: Optional[str] = None
) -> Union[list, Generator[list, None, None]]:
    """
    Queries database for vaules in sql table column.
    Returns list of values in sql table column.
    Returns a lists of values.
    Returns a generator of lists of values if chunksize is not None.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    column_name: str
        name of sql table column.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    chunksize: int, default None
        if not None, returns generator of lists of values.
    
    Returns
    -------
    list of sql table column values or generator of lists of values.
    """
    table = _get_table(table, connection, schema=schema)
    if chunksize is None:
        return select_column_values_all(table, column_name, connection)
    else:
        return select_column_values_chunks(table, column_name, connection, chunksize)


def select_column_values_all(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    column_name: str,
    schema: Optional[str] = None
) -> list:
    """
    Queries database for vaules in sql table column.
    Returns list of values in sql table column.
    Returns a lists of values.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    column_name: str
        name of sql table column.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    
    Returns
    -------
    list of sql table column values.
    """
    table = _get_table(table, connection, schema=schema)
    query = select(table.c[column_name])
    return connection.execute(query).scalars().all()


def select_column_values_chunks(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    column_name: str,
    chunksize: int,
    schema: Optional[str] = None
) -> Generator[list, None, None]:
    """
    Queries database for vaules in sql table column.
    Returns a generator of lists of values.
    
    Parameters
    ----------
    table: sa.Table
        SqlAlchemy table mapped to sql table.
    column_name: str
        name of sql table column.
    connection: sa.engine.Engine, sa.orm.Session, or sa.engine.Connection
        connection used to query database.
    chunksize: int, default None
        Returns generator of chunksized lists of values.
    
    Returns
    -------
    Generator of chunksized lists of sql table column values.
    """
    table = _get_table(table, connection, schema=schema)
    query = select(table.c[column_name])
    stream = connection.execute(query, execution_options={'stream_results': True})
    for results in stream.scalars().partitions(chunksize):
        yield results


def _calc_positive_index(index: int, row_count: int) -> int:
    # convert negative index to real index
    if index < 0:
        index = row_count + index
    return index


def _stop_overflow_index(index: int, row_count: int) -> int:
    if index > row_count - 1:
        return row_count
    return index

    
def _stop_underflow_index(index: int, row_count: int) -> int:
    if index < 0 and index < -row_count:
        return 0
    return index


def _convert_slice_indexes(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    start: Optional[int] = None,
    stop: Optional[int] = None,
    schema: Optional[str] = None
) -> tuple[int, int]:
    table = _get_table(table, connection, schema=schema)
    # start index is 0 if None
    start = 0 if start is None else start
    row_count = get_row_count(table, connection)
    
    # stop index is row count if None
    stop = row_count if stop is None else stop
    # convert negative indexes
    start = _calc_positive_index(start, row_count)
    start = _stop_underflow_index(start, row_count)
    stop = _calc_positive_index(stop, row_count)
    stop = _stop_overflow_index(stop, row_count)

    if row_count == 0:
        return 0, 0

    return start, stop


def select_records_slice(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    start: Optional[int] = None,
    stop: Optional[int] = None,
    schema: Optional[str] = None,
    sorted: bool = False,
    include_columns: Optional[list[str]] = None
) -> list[Record]:
    """

    start: Starting index where the slicing of table records starts.
    stop: Ending index where the slicing of table records stops. Non-inclusive.

    The index is not necessarily the primary key value.
    0 is always the first record's index.
    -1 is always the last record's index.

    start is optional, is 0 if None
    stop is optional, is the last index + 1 if None.

    """
    table = _get_table(table, connection, schema=schema)
    start, stop = _convert_slice_indexes(table, connection, start, stop)
    if stop < start:
        raise SliceError('stop cannot be less than start.')
    if include_columns is not None:
        columns = [get_column(table, column_name) for column_name in include_columns]
        query = select(*columns)
    else:
        query = select(table)
    if sorted:
        query = query.order_by(*table.primary_key.columns.values())
    query = query.slice(start, stop)
    results = connection.execute(query)
    return [dict(r) for r in results]


def select_record_by_index(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    index: int,
    schema: Optional[str] = None,
    include_columns: Optional[list[str]] = None
) -> Record:
    """
    Select a record by index.
    """
    table = _get_table(table, connection, schema=schema)
    if index < 0:
        row_count = get_row_count(table, connection)
        if index < -row_count:
            raise IndexError('Index out of range.') 
        index = _calc_positive_index(index, row_count)
    records = select_records_slice(table, connection, index, index+1, include_columns=include_columns)
    if len(records) == 0:
        raise IndexError('Index out of range.')
    return records[0]


def select_first_record(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    schema: Optional[str] = None,
    include_columns: Optional[list[str]] = None
) -> Union[dict, None]:
    """
    Select first record in table
    Returns dictionary or
    Returns None if table is empty
    """
    table = _get_table(table, connection, schema=schema)
    for chunk in select_records(table, connection, chunksize=1, include_columns=include_columns):
        return chunk[0]
    return None


def select_column_values_by_slice(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    column_name: str,
    start: Optional[int] = None,
    stop: Optional[int] = None,
    schema: Optional[str] = None
) -> list:
    """
    Select a subset of column values by slice.
    """
    table = _get_table(table, connection, schema=schema)
    start, stop = _convert_slice_indexes(table, connection, start, stop)
    if stop < start:
        raise SliceError('stop cannot be less than start.')
    query = select(table.c[column_name]).slice(start, stop)
    return connection.execute(query).scalars().all()


def select_column_value_by_index(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    column_name: str,
    index: int,
    schema: Optional[str] = None
) -> Any:
    """
    Select a column value by index.
    """
    table = _get_table(table, connection, schema=schema)
    if index < 0:
        row_count = get_row_count(table, connection)
        if index < -row_count:
            raise IndexError('Index out of range.') 
        index = _calc_positive_index(index, row_count)
    query = select(table.c[column_name]).slice(index, index+1)
    return connection.execute(query).scalars().all()[0]


def select_primary_key_records_by_slice(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    _slice: slice,
    schema: Optional[str] = None,
    sorted: bool = False
) -> list[Record]:
    """
    Select primary key values by slice.
    """
    start = _slice.start
    stop = _slice.stop
    table = _get_table(table, connection, schema=schema)
    start, stop = _convert_slice_indexes(table, connection, start, stop)
    if stop < start:
        raise SliceError('stop cannot be less than start.')
    if sorted:
        query = select(table.primary_key.columns.values()).order_by(*table.primary_key.columns.values()).slice(start, stop)
    else:
        query = select(table.primary_key.columns.values()).slice(start, stop)
    results = connection.execute(query)
    return [dict(r) for r in results]


def select_primary_key_values(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    schema: Optional[str] = None
) -> list[Record]:
    table = _get_table(table, connection, schema=schema)
    return select_primary_key_records_by_slice(table, connection, slice(None, None))


def select_primary_key_record_by_index(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    index: int,
    schema: Optional[str] = None
) -> Record:
    """
    Select primary key values by index.
    """
    table = _get_table(table, connection, schema=schema)
    if index < 0:
        row_count = get_row_count(table, connection)
        if index < -row_count:
            raise IndexError('Index out of range.') 
        index = _calc_positive_index(index, row_count)
    return select_primary_key_records_by_slice(table, connection, slice(index, index+1))[0]


def check_slice_primary_keys_match(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    start: int,
    stop: int,
    records: list[Record],
    schema: Optional[str] = None
) -> bool:
    """
    Check if records have matching primary key values to slice of table records
    """
    table = _get_table(table, connection, schema=schema)
    slice_key_values = select_primary_key_records_by_slice(table, connection, slice(start, stop))
    keys = primary_keys(table)
    records_key_values = [{key:record[key] for key in keys} for record in records]

    if len(slice_key_values) != len(records_key_values):
        return False

    for slice_key_value in slice_key_values:
        if slice_key_value not in records_key_values:
            return False

    return True


def check_index_keys_match(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    index: int,
    record: Record,
    schema: Optional[str] = None
) -> bool:
    """
    Check if record's primary key values match index table record.
    """
    table = _get_table(table, connection, schema=schema)
    keys = primary_keys(table)
    key_record = select_primary_key_record_by_index(table, connection, index)
    return {key:record[key] for key in keys} == key_record


def select_record_by_primary_key(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    primary_key_value: Record,
    schema: Optional[str] = None,
    include_columns: Optional[list[str]] = None
) -> Record:
    """
    Select a record by primary key values
    """
    table = _get_table(table, connection, schema=schema)
    keys = primary_keys(table)
    # TODO: check if primary key values exist

    where_clause = [table.c[key_name]==key_value for key_name, key_value in primary_key_value.items()]
    if len(where_clause) == 0:
        return []
    if include_columns is not None:
        columns = [get_column(table, column_name) for column_name in include_columns]
        query = select(*columns).where((and_(*where_clause)))
    else:
        query = select(table).where((and_(*where_clause)))
    results = connection.execute(query)
    results = [dict(x) for x in results]
    if len(results) == 0:
        raise MissingPrimaryKey('Primary key values missing in table.')
    return results[0]


def select_records_by_primary_keys(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    primary_keys_values: list[Record],
    schema: Optional[str] = None,
    include_columns: Optional[list[str]] = None
) -> list[Record]:
    """
    Select the records that match the primary key values
    """
    table = _get_table(table, connection, schema=schema)
    keys = primary_keys(table)
    # TODO: check if primary key values exist

    where_clauses = []
    for record in primary_keys_values:
        where_clause = [table.c[key_name]==key_value for key_name, key_value in record.items()]
        where_clauses.append(and_(*where_clause))
    if len(where_clauses) == 0:
        return []
    if include_columns is not None:
        columns = [get_column(table, column_name) for column_name in include_columns]
        query = select(*columns).where((or_(*where_clauses)))
    else:
        query = select(table).where((or_(*where_clauses)))
    results = connection.execute(query)
    return [dict(r) for r in results]


def select_column_values_by_primary_keys(
    table: sa.Table,
    connection: SqlConnection,
    column_name: str,
    primary_keys_values: list[Record]
) -> list:
    """
    Select multiple values from a column by primary key values
    """
    keys = primary_keys(table)
    # TODO: check if primary key values exist

    where_clauses = []
    for record in primary_keys_values:
        where_clause = [table.c[key_name]==key_value for key_name, key_value in record.items()]
        where_clauses.append(and_(*where_clause))

    if len(where_clauses) == 0:
        return []
    query = select(table.c[column_name]).where((or_(*where_clauses)))
    results = connection.execute(query)
    return results.scalars().fetchall()


def select_value_by_primary_keys(
    table: Union[sa.Table, str],
    connection: SqlConnection,
    column_name: str,
    primary_key_value: Record,
    schema: Optional[str] = None
) -> Any:
    """
    Select a single value from a column by primary key values
    """
    table = _get_table(table, connection, schema=schema)
    keys = primary_keys(table)
    # TODO: check if primary key values exist

    where_clause = [table.c[key_name]==key_value for key_name, key_value in primary_key_value.items()]
    if len(where_clause) == 0:
        raise KeyError('No such primary key values exist in table.')
    query = select(table.c[column_name]).where((and_(*where_clause)))
    return connection.execute(query).scalars().all()[0]