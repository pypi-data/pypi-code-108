import os
import random
import string
import configparser
from logging import getLogger
from tempfile import TemporaryDirectory
from typing import Optional, Tuple, Sequence, TypeVar, Iterator

import pandas as pd
import snowflake.connector
from snowflake.connector import ProgrammingError, SnowflakeConnection

getLogger("snowflake.connector.cursor").disabled = True
getLogger("snowflake.connector.connection").disabled = True
getLogger("snowflake.connector.network").disabled = True
logger = getLogger(__name__)

def write_pandas_binary(
    conn: "SnowflakeConnection",
    df: "pandas.DataFrame",
    table_name: str,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    chunk_size: Optional[int] = None,
    compression: str = "gzip",
    on_error: str = "abort_statement",
    parallel: int = 4,
    quote_identifiers: bool = True,
) -> Tuple[
    bool,
    int,
    int,
    Sequence[
        Tuple[
            str,
            str,
            int,
            int,
            int,
            int,
            Optional[str],
            Optional[int],
            Optional[int],
            Optional[str],
        ]
    ],
]:
    """Allows users to most efficiently write back a pandas DataFrame to Snowflake.

    It works by dumping the DataFrame into Parquet files, uploading them and finally copying their data into the table.

    Returns whether all files were ingested correctly, number of chunks uploaded, and number of rows ingested
    with all of the COPY INTO command's output for debugging purposes.

        Example usage:
            import pandas
            from snowflake.connector.pandas_tools import write_pandas

            df = pandas.DataFrame([('Mark', 10), ('Luke', 20)], columns=['name', 'balance'])
            success, nchunks, nrows, _ = write_pandas(cnx, df, 'customers')

    Args:
        conn: Connection to be used to communicate with Snowflake.
        df: Dataframe we'd like to write back.
        table_name: Table name where we want to insert into.
        database: Database schema and table is in, if not provided the default one will be used (Default value = None).
        schema: Schema table is in, if not provided the default one will be used (Default value = None).
        chunk_size: Number of elements to be inserted once, if not provided all elements will be dumped once
            (Default value = None).
        compression: The compression used on the Parquet files, can only be gzip, or snappy. Gzip gives supposedly a
            better compression, while snappy is faster. Use whichever is more appropriate (Default value = 'gzip').
        on_error: Action to take when COPY INTO statements fail, default follows documentation at:
            https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html#copy-options-copyoptions
            (Default value = 'abort_statement').
        parallel: Number of threads to be used when uploading chunks, default follows documentation at:
            https://docs.snowflake.com/en/sql-reference/sql/put.html#optional-parameters (Default value = 4).
        quote_identifiers: By default, identifiers, specifically database, schema, table and column names
            (from df.columns) will be quoted. If set to False, identifiers are passed on to Snowflake without quoting.
            I.e. identifiers will be coerced to uppercase by Snowflake.  (Default value = True)

    Returns:
        Returns the COPY INTO command's results to verify ingestion in the form of a tuple of whether all chunks were
        ingested correctly, # of chunks, # of ingested rows, and ingest's output.
    """
    if database is not None and schema is None:
        raise ProgrammingError(
            "Schema has to be provided to write_pandas when a database is provided"
        )
    # This dictionary maps the compression algorithm to Snowflake put copy into command type
    # https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html#type-parquet
    compression_map = {"gzip": "auto", "snappy": "snappy"}
    if compression not in compression_map.keys():
        raise ProgrammingError(
            "Invalid compression '{}', only acceptable values are: {}".format(
                compression, compression_map.keys()
            )
        )
    if quote_identifiers:
        location = (
            (('"' + database + '".') if database else "")
            + (('"' + schema + '".') if schema else "")
            + ('"' + table_name + '"')
        )
    else:
        location = (
            (database + "." if database else "")
            + (schema + "." if schema else "")
            + (table_name)
        )
    if chunk_size is None:
        chunk_size = len(df)
    cursor = conn.cursor()
    stage_name = None  # Forward declaration
    while True:
        try:
            stage_name = "".join(
                random.choice(string.ascii_lowercase) for _ in range(5)
            )
            create_stage_sql = (
                "create temporary stage /* Python:snowflake.connector.pandas_tools.write_pandas() */ "
                '"{stage_name}"'
            ).format(stage_name=stage_name)
            logger.debug("creating stage with '{}'".format(create_stage_sql))
            cursor.execute(create_stage_sql, _is_internal=True).fetchall()
            break
        except ProgrammingError as pe:
            if pe.msg.endswith("already exists."):
                continue
            raise

    with TemporaryDirectory() as tmp_folder:
        for i, chunk in chunk_helper(df, chunk_size):
            chunk_path = os.path.join(tmp_folder, "file{}.txt".format(i))
            # Dump chunk into parquet file
            chunk.to_parquet(chunk_path, compression=compression)
            # Upload parquet file
            upload_sql = (
                "PUT /* Python:snowflake.connector.pandas_tools.write_pandas() */ "
                "'file://{path}' @\"{stage_name}\" PARALLEL={parallel}"
            ).format(
                path=chunk_path.replace("\\", "\\\\").replace("'", "\\'"),
                stage_name=stage_name,
                parallel=parallel,
            )
            logger.debug("uploading files with '{}'".format(upload_sql))
            cursor.execute(upload_sql, _is_internal=True)
            # Remove chunk file
            os.remove(chunk_path)
    if quote_identifiers:
        columns = '"' + '","'.join(list(df.columns)) + '"'
    else:
        columns = ",".join(list(df.columns))

    # in Snowflake, all parquet data is stored in a single column, $1, so we must select columns explicitly
    # see (https://docs.snowflake.com/en/user-guide/script-data-load-transform-parquet.html)
    if quote_identifiers:
        parquet_columns = ",".join(f'TO_BINARY($1:"{c}")' if c in ['entity_key','value'] else f'$1:"{c}"' for c in df.columns)
    else:
        parquet_columns = ",".join(f'TO_BINARY($1:{c})' if c in ['entity_key','value'] else f'$1:{c}' for c in df.columns)

    copy_into_sql = (
        "COPY INTO {location} /* Python:snowflake.connector.pandas_tools.write_pandas() */ "
        "({columns}) "
        'FROM (SELECT {parquet_columns} FROM @"{stage_name}") '
        "FILE_FORMAT=(TYPE=PARQUET COMPRESSION={compression} BINARY_AS_TEXT = FALSE) "
        "PURGE=TRUE ON_ERROR={on_error}"
    ).format(
        location=location,
        columns=columns,
        parquet_columns=parquet_columns,
        stage_name=stage_name,
        compression=compression_map[compression],
        on_error=on_error,
    )
    logger.debug("copying into with '{}'".format(copy_into_sql))
    copy_results = cursor.execute(copy_into_sql, _is_internal=True).fetchall()
    cursor.close()
    return (
        all(e[1] == "LOADED" for e in copy_results),
        len(copy_results),
        sum(int(e[3]) for e in copy_results),
        copy_results,
    )


def create_new_snowflake_table(
    conn: SnowflakeConnection,
    df: pd.DataFrame,
    table_name: str,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    compression: str = "gzip",
    on_error: str = "abort_statement",
    parallel: int = 4,
    quote_identifiers: bool = True,
    alt_table_type: str = "permanent",
) -> None:
    cur = conn.cursor()

    result = cur.execute('SELECT * FROM "INFORMATION_SCHEMA"."TABLES"')
    table_names = result.fetch_pandas_all()
    if table_name not in list(
        table_names[table_names["TABLE_SCHEMA"] == conn._schema]["TABLE_NAME"]
    ):

        if database is not None and schema is None:
            raise ProgrammingError(
                "Schema has to be provided to create_new_snowflake_table when a database is provided"
            )

        compression_map = {"gzip": "auto", "snappy": "snappy"}
        if compression not in compression_map.keys():
            raise ProgrammingError(
                "Invalid compression '{}', only acceptable values are: {}".format(
                    compression, compression_map.keys()
                )
            )

        if quote_identifiers:
            location = (
                (('"' + database + '".') if database else "")
                + (('"' + schema + '".') if schema else "")
                + ('"' + table_name + '"')
            )
        else:
            location = (
                (database + "." if database else "")
                + (schema + "." if schema else "")
                + (table_name)
            )

        stage_name = None  # Forward declaration
        while True:
            try:
                stage_name = "".join(
                    random.choice(string.ascii_lowercase) for _ in range(5)
                )
                create_stage_sql = (
                    "create temporary stage /* Python:snowflake.connector.pandas_tools.create_new_snowflake_table() */ "
                    '"{stage_name}"'
                ).format(stage_name=stage_name)
                logger.debug("creating stage with '{}'".format(create_stage_sql))
                cur.execute(create_stage_sql, _is_internal=True).fetchall()
                break
            except ProgrammingError as pe:
                if pe.msg.endswith("already exists."):
                    continue
                raise

        with TemporaryDirectory() as tmp_folder:

            chunk_path = os.path.join(tmp_folder, "file{}.txt".format(0))
            # Dump chunk into parquet file
            df.head().to_parquet(
                chunk_path,
                compression=compression,
                use_deprecated_int96_timestamps=True,
            )
            # Upload parquet file
            upload_sql = (
                "PUT /* Python:snowflake.connector.pandas_tools.create_new_snowflake_table() */ "
                "'file://{path}' @\"{stage_name}\" PARALLEL={parallel}"
            ).format(
                path=chunk_path.replace("\\", "\\\\").replace("'", "\\'"),
                stage_name=stage_name,
                parallel=parallel,
            )
            logger.debug("uploading files with '{}'".format(upload_sql))
            cur.execute(upload_sql, _is_internal=True)
            # Remove chunk file
            os.remove(chunk_path)

        alt_table_types = ["permanent", "transient", "temporary"]
        if alt_table_type.lower() not in alt_table_types:
            raise ProgrammingError(
                "Invalid table type '{}', only acceptable values are: {}".format(
                    alt_table_type, alt_table_types
                )
            )

        table_type_name = ""
        if alt_table_type.lower() in ["transient", "temporary"]:
            table_type_name = alt_table_type.upper()

        # If the table doesnt exists, we need to create it
        file_format_name = "".join(
            random.choice(string.ascii_lowercase) for _ in range(5)
        )

        ff_sql = f"""
        CREATE TEMPORARY FILE FORMAT "{file_format_name}" /* Python:snowflake.connector.pandas_tools.create_new_snowflake_table() */
            TYPE = PARQUET;
        """

        logger.debug("creating parquet file format with '{}'".format(ff_sql))
        cur.execute(ff_sql, _is_internal=True)

        table_sql = f"""
        CREATE {table_type_name} TABLE {location} USING TEMPLATE /* Python:snowflake.connector.pandas_tools.create_new_snowflake_table() */
            (
            SELECT
                ARRAY_AGG(OBJECT_CONSTRUCT(*))
            FROM
                TABLE(
                    INFER_SCHEMA(
                      LOCATION=>'@"{stage_name}"',
                      FILE_FORMAT=>'"{file_format_name}"'
                    )
                )
            );
        """

        logger.debug(
            "creating new table if one doesnt exist with '{}'".format(table_sql)
        )
        cur.execute(table_sql, _is_internal=True)

        cur.close()
    else:
        raise Exception("Table already exists")
    return None


def get_snowflake_conn(config) -> SnowflakeConnection:

    if config.type == 'feast_snowflake.SnowflakeOfflineStore':
        config_header = 'connections.feast_offline_store'
    elif config.type == 'feast_snowflake.SnowflakeOnlineStore':
        config_header = 'connections.feast_online_store'

    config = dict(config)

    #read config file
    config_reader = configparser.ConfigParser()
    config_reader.read([config['config_path']])
    if config_reader.has_section(config_header):
        kwargs = dict(config_reader[config_header])
    else:
        kwargs = {}

    kwargs.update( (k,v) for k,v in config.items() if v is not None)

    try:
        conn = snowflake.connector.connect(
            account=kwargs['account'],
            user=kwargs['user'],
            password=kwargs['password'],
            role=f'''"{kwargs['role']}"''',
            warehouse=f'''"{kwargs['warehouse']}"''',
            database=f'''"{kwargs['database']}"''',
            schema=f'''"{kwargs['schema_']}"''',
            application="feast",
            autocommit=False,)

        return conn
    except KeyError as e:
        print(f'{e} not defined in a config file or feature_store.yaml file')


def write_pandas(
    conn: "SnowflakeConnection",
    df: "pandas.DataFrame",
    table_name: str,
    database: Optional[str] = None,
    schema: Optional[str] = None,
    chunk_size: Optional[int] = None,
    compression: str = "gzip",
    on_error: str = "abort_statement",
    parallel: int = 4,
    quote_identifiers: bool = True,
) -> Tuple[
    bool,
    int,
    int,
    Sequence[
        Tuple[
            str,
            str,
            int,
            int,
            int,
            int,
            Optional[str],
            Optional[int],
            Optional[int],
            Optional[str],
        ]
    ],
]:
    """Allows users to most efficiently write back a pandas DataFrame to Snowflake.

    It works by dumping the DataFrame into Parquet files, uploading them and finally copying their data into the table.

    Returns whether all files were ingested correctly, number of chunks uploaded, and number of rows ingested
    with all of the COPY INTO command's output for debugging purposes.

        Example usage:
            import pandas
            from snowflake.connector.pandas_tools import write_pandas

            df = pandas.DataFrame([('Mark', 10), ('Luke', 20)], columns=['name', 'balance'])
            success, nchunks, nrows, _ = write_pandas(cnx, df, 'customers')

    Args:
        conn: Connection to be used to communicate with Snowflake.
        df: Dataframe we'd like to write back.
        table_name: Table name where we want to insert into.
        database: Database schema and table is in, if not provided the default one will be used (Default value = None).
        schema: Schema table is in, if not provided the default one will be used (Default value = None).
        chunk_size: Number of elements to be inserted once, if not provided all elements will be dumped once
            (Default value = None).
        compression: The compression used on the Parquet files, can only be gzip, or snappy. Gzip gives supposedly a
            better compression, while snappy is faster. Use whichever is more appropriate (Default value = 'gzip').
        on_error: Action to take when COPY INTO statements fail, default follows documentation at:
            https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html#copy-options-copyoptions
            (Default value = 'abort_statement').
        parallel: Number of threads to be used when uploading chunks, default follows documentation at:
            https://docs.snowflake.com/en/sql-reference/sql/put.html#optional-parameters (Default value = 4).
        quote_identifiers: By default, identifiers, specifically database, schema, table and column names
            (from df.columns) will be quoted. If set to False, identifiers are passed on to Snowflake without quoting.
            I.e. identifiers will be coerced to uppercase by Snowflake.  (Default value = True)

    Returns:
        Returns the COPY INTO command's results to verify ingestion in the form of a tuple of whether all chunks were
        ingested correctly, # of chunks, # of ingested rows, and ingest's output.
    """
    if database is not None and schema is None:
        raise ProgrammingError(
            "Schema has to be provided to write_pandas when a database is provided"
        )
    # This dictionary maps the compression algorithm to Snowflake put copy into command type
    # https://docs.snowflake.com/en/sql-reference/sql/copy-into-table.html#type-parquet
    compression_map = {"gzip": "auto", "snappy": "snappy"}
    if compression not in compression_map.keys():
        raise ProgrammingError(
            "Invalid compression '{}', only acceptable values are: {}".format(
                compression, compression_map.keys()
            )
        )
    if quote_identifiers:
        location = (
            (('"' + database + '".') if database else "")
            + (('"' + schema + '".') if schema else "")
            + ('"' + table_name + '"')
        )
    else:
        location = (
            (database + "." if database else "")
            + (schema + "." if schema else "")
            + (table_name)
        )
    if chunk_size is None:
        chunk_size = len(df)
    cursor = conn.cursor()
    stage_name = None  # Forward declaration
    while True:
        try:
            stage_name = "".join(
                random.choice(string.ascii_lowercase) for _ in range(5)
            )
            create_stage_sql = (
                "create temporary stage /* Python:snowflake.connector.pandas_tools.write_pandas() */ "
                '"{stage_name}"'
            ).format(stage_name=stage_name)
            logger.debug("creating stage with '{}'".format(create_stage_sql))
            cursor.execute(create_stage_sql, _is_internal=True).fetchall()
            break
        except ProgrammingError as pe:
            if pe.msg.endswith("already exists."):
                continue
            raise

    with TemporaryDirectory() as tmp_folder:
        for i, chunk in chunk_helper(df, chunk_size):
            chunk_path = os.path.join(tmp_folder, "file{}.txt".format(i))
            # Dump chunk into parquet file
            chunk.to_parquet(chunk_path, compression=compression, use_deprecated_int96_timestamps=True,)
            # Upload parquet file
            upload_sql = (
                "PUT /* Python:snowflake.connector.pandas_tools.write_pandas() */ "
                "'file://{path}' @\"{stage_name}\" PARALLEL={parallel}"
            ).format(
                path=chunk_path.replace("\\", "\\\\").replace("'", "\\'"),
                stage_name=stage_name,
                parallel=parallel,
            )
            logger.debug("uploading files with '{}'".format(upload_sql))
            cursor.execute(upload_sql, _is_internal=True)
            # Remove chunk file
            os.remove(chunk_path)
    if quote_identifiers:
        columns = '"' + '","'.join(list(df.columns)) + '"'
    else:
        columns = ",".join(list(df.columns))

    # in Snowflake, all parquet data is stored in a single column, $1, so we must select columns explicitly
    # see (https://docs.snowflake.com/en/user-guide/script-data-load-transform-parquet.html)
    if quote_identifiers:
        parquet_columns = "$1:" + ",$1:".join(f'"{c}"' for c in df.columns)
    else:
        parquet_columns = "$1:" + ",$1:".join(df.columns)
    copy_into_sql = (
        "COPY INTO {location} /* Python:snowflake.connector.pandas_tools.write_pandas() */ "
        "({columns}) "
        'FROM (SELECT {parquet_columns} FROM @"{stage_name}") '
        "FILE_FORMAT=(TYPE=PARQUET COMPRESSION={compression}) "
        "PURGE=TRUE ON_ERROR={on_error}"
    ).format(
        location=location,
        columns=columns,
        parquet_columns=parquet_columns,
        stage_name=stage_name,
        compression=compression_map[compression],
        on_error=on_error,
    )
    logger.debug("copying into with '{}'".format(copy_into_sql))
    copy_results = cursor.execute(copy_into_sql, _is_internal=True).fetchall()
    cursor.close()
    return (
        all(e[1] == "LOADED" for e in copy_results),
        len(copy_results),
        sum(int(e[3]) for e in copy_results),
        copy_results,
    )

T = TypeVar("T", bound=Sequence)

def chunk_helper(lst: T, n: int) -> Iterator[Tuple[int, T]]:
    """Helper generator to chunk a sequence efficiently with current index like if enumerate was called on sequence."""
    for i in range(0, len(lst), n):
        yield int(i / n), lst[i : i + n]
