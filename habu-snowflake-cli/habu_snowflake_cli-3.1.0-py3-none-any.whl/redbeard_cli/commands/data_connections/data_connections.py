import json
import uuid
from typing import List

from redbeard_cli import snowflake_utils
from redbeard_cli.commands.data_connections import utils


def ls(sf_connection):
    data_connections = utils.fetch_connections(sf_connection)
    for dc in data_connections:
        print(dc)


def inspect(sf_connection, db_name: str, db_schema: str, db_table: str):
    table_columns = utils.fetch_table_columns(sf_connection, db_name, db_schema, db_table)
    for col in table_columns:
        print(json.dumps(col))


def add(sf_connection, organization_id: str, db_name: str, db_schema: str,
        db_table: str, dataset_type: str, identity_type: str,
        identity_column: str, lookup_columns: List[str]) -> bool:
    all_columns = [identity_column]
    for c in lookup_columns:
        all_columns.append(c)
    if not utils.validate_data_connection_request(sf_connection, db_name, db_schema, db_table, all_columns):
        return False

    # the customer database that contains the table (or view) for the data connection must be
    # shared with Habu (via HABU_DATA_CONNECTIONS_SHARE) using REFERENCE_USAGE
    snowflake_utils.run_query(
        sf_connection,
        "GRANT REFERENCE_USAGE ON DATABASE %s TO SHARE HABU_DATA_CONNECTIONS_SHARE" % db_name
    )

    dc_id = str(uuid.uuid4())
    snowflake_utils.run_query(
        sf_connection,
        """
        INSERT INTO HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.DATA_CONNECTIONS 
        (ID, ORGANIZATION_ID, DATABASE_NAME, DB_SCHEMA_NAME, DB_TABLE_NAME, DATASET_TYPE, IDENTITY_TYPE)
        (
          SELECT :DCID:, :ORGID:, 
                 TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME, :DSTYPE:, :IDTYPE:
          FROM %s.INFORMATION_SCHEMA.TABLES
          WHERE TABLE_CATALOG = :DBNAME: AND TABLE_SCHEMA = :DBSCHEMA: AND TABLE_NAME = :DBTABLE:
        )""" % db_name,
        [
            ("DCID", dc_id),
            ("ORGID", organization_id),
            ("DSTYPE", dataset_type),
            ("IDTYPE", identity_type),
            ("DBNAME", db_name),
            ("DBSCHEMA", db_schema),
            ("DBTABLE", db_table),
        ]
    )

    snowflake_utils.run_query(
        sf_connection,
        """INSERT INTO HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.DATA_CONNECTION_COLUMNS
        (ID, ORGANIZATION_ID, DATA_CONNECTION_ID, COLUMN_NAME, COLUMN_POSITION, DATA_TYPE, IS_LOOKUP_COLUMN, IS_IDENTITY_COLUMN)
        (
          SELECT uuid_string(), :ORGID:, :DCID:, 
          COLUMN_NAME, ORDINAL_POSITION, DATA_TYPE, FALSE, FALSE
          FROM %s.INFORMATION_SCHEMA.COLUMNS
          WHERE TABLE_CATALOG = :DBNAME: AND TABLE_SCHEMA = :DBSCHEMA: AND TABLE_NAME = :DBTABLE:  
        )""" % db_name,
        [
            ("ORGID", organization_id),
            ("DCID", dc_id),
            ("DBNAME", db_name),
            ("DBSCHEMA", db_schema),
            ("DBTABLE", db_table)
        ]
    )

    for column in lookup_columns:
        snowflake_utils.run_query(
            sf_connection,
            """UPDATE HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.DATA_CONNECTION_COLUMNS 
            SET IS_LOOKUP_COLUMN = :IS_LOOKUP_COLUMN: 
            WHERE DATA_CONNECTION_ID = :DCID: AND ORGANIZATION_ID = :ORGID: 
            AND COLUMN_NAME = :DBCOLUMN:""",
            [
                ("IS_LOOKUP_COLUMN", "TRUE"),
                ("DCID", dc_id),
                ("ORGID", organization_id),
                ("DBCOLUMN", column.upper())
            ]
        )

    snowflake_utils.run_query(
        sf_connection,
        """UPDATE HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.DATA_CONNECTION_COLUMNS 
        SET IS_IDENTITY_COLUMN = :IS_IDENTITY_COLUMN: 
        WHERE DATA_CONNECTION_ID = :DCID: AND ORGANIZATION_ID = :ORGID: 
        AND COLUMN_NAME = :DBCOLUMN:""",
        [
            ("IS_IDENTITY_COLUMN", "TRUE"),
            ("DCID", dc_id),
            ("ORGID", organization_id),
            ("DBCOLUMN", identity_column.upper())
        ]
    )

    av_sql = """CREATE OR REPLACE SECURE VIEW HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.V_%s_%s_%s
    AS SELECT %s, COUNT(*) AS VALUE_COUNT FROM %s.%s.%s GROUP BY %s""" % (db_name, db_schema, db_table, ', '.join(lookup_columns), db_name, db_schema, db_table, ','.join([str(x) for x in range(1, len(lookup_columns) + 1)]))

    snowflake_utils.run_query(sf_connection, av_sql)

    snowflake_utils.run_query(
        sf_connection,
        """GRANT SELECT ON VIEW HABU_DATA_CONNECTIONS.DATA_CONNECTIONS.V_%s_%s_%s
        TO SHARE HABU_DATA_CONNECTIONS_SHARE""" % (db_name, db_schema, db_table)
    )
    return True
