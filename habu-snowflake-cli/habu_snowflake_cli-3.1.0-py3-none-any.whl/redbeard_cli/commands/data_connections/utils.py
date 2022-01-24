from typing import List, Dict, Any

from snowflake.connector import DictCursor

from redbeard_cli import snowflake_utils


def validate_data_connection_request(sf_connection, db_name: str, db_schema: str,
                                     db_table: str, input_table_columns: List[str]) -> bool:
    data_connections = fetch_connections(sf_connection)
    dc_name = '%s.%s.%s' % (db_name, db_schema, db_table)
    if dc_name in data_connections:
        print("Data Connection %s has already been added." % dc_name)
        return False

    col_names = [x['name'] for x in fetch_table_columns(sf_connection, db_name, db_schema, db_table)]
    table_columns = set(col_names)
    missing_columns = []
    for column in input_table_columns:
        if column not in table_columns:
            missing_columns.append(column)

    if len(missing_columns) > 0:
        print("""*** Table Columns list is not valid. ***  
        The following columns were not found in %s: %s""" % (dc_name, ', '.join(missing_columns)))
        return False
    return True


def fetch_connections(sf_connection):
    data_connections = set()
    cur = sf_connection.cursor(DictCursor)
    try:
        cur.execute("""SELECT database_name, db_schema_name, db_table_name 
        FROM HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.DATA_CONNECTIONS""")
        for rec in cur:
            db_name = snowflake_utils.get_column_value(rec, 'database_name')
            schema_name = snowflake_utils.get_column_value(rec, 'db_schema_name')
            table_name = snowflake_utils.get_column_value(rec, 'db_table_name')
            data_connections.add('%s.%s.%s' % (db_name, schema_name, table_name))
    finally:
        cur.close()
    return data_connections


def fetch_table_columns(sf_connection, db: str, schema: str, db_table: str) -> List[Dict[str, Any]]:
    columns = []
    cur = sf_connection.cursor(DictCursor)
    try:
        cur.execute(
            """SELECT ORDINAL_POSITION, COLUMN_NAME, DATA_TYPE FROM %s.INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_CATALOG = :1 AND TABLE_SCHEMA = :2 AND TABLE_NAME = :3 ORDER BY ORDINAL_POSITION""" % db,
            [db, schema, db_table]
        )
        for rec in cur:
            columns.append({
                'position': snowflake_utils.get_column_value(rec, "ordinal_position"),
                'name': snowflake_utils.get_column_value(rec, "column_name"),
                'data_type': snowflake_utils.get_column_value(rec, "data_type")
            })
    finally:
        cur.close()
    return columns
