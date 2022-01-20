from converter.config.config_converter import excluded_fields, base_converter_params
import logging
import sys
import sqlalchemy
import warnings
from sqlalchemy.engine import create_engine
from sqlalchemy import MetaData, Table
from converter.vertica.custom_insert import vertica_insert
from converter.vertica.merge import vertica_merge

warnings.filterwarnings("ignore")


def get_type_sql_alchemy(type):
    try:
        return str(type.nested_type.__visit_name__).lower()
    except BaseException:
        return str(type.__visit_name__).lower()


def get_length_type_sql_alchemy(type):
    try:
        return type.length
    except BaseException:
        None


def get_default_arg_sql_alchemy(column):
    if column.default is not None:
        return column.default.arg
    elif column.server_default is not None:
        return str(column.server_default.arg)


class DataBaseWorker:
    def __init__(
            self, sql_credentials, db, debug=True, tables=None, table_checker=True
    ):
        """
        :param sql_credentials:
        :param debug: show debug text
        :param tables: converter only for list of tables. Will process more rapidly
        """
        log_format = "%(asctime)-15s %(name)s:%(levelname)s: %(message)s"
        logging.basicConfig(format=log_format, stream=sys.stdout, level=logging.INFO)
        logging.basicConfig(format=log_format, stream=sys.stderr, level=logging.ERROR)
        logging.captureWarnings(True)
        self.logger = logging.getLogger(__class__.__name__)

        self.table_checker = table_checker
        self.tables = tables or []
        self.table_name = None
        self.db = db
        self.debug = debug
        self.sql_credentials = sql_credentials
        self.cred = self.sql_credentials[self.db]
        self.conn = None
        if self.__check_dialect():
            uri_sql_alchemy = "{0}://{1}:{2}@{3}:{4}/{5}".format(
                self.dialect,
                self.cred["user"],
                self.cred["password"],
                self.cred["host"],
                self.cred["port"],
                self.cred["database"],
            )
        additional_args = {}
        for key in self.sql_credentials[self.db]:
            if key not in ["database", "schema", "user", "host", "password", "port"]:
                additional_args[key] = self.sql_credentials[self.db][key]
        self.engine = create_engine(uri_sql_alchemy, **additional_args)
        if "schema" in self.cred:
            self.schema = self.cred["schema"]
        else:
            self.schema = self.cred["database"]
        self.logger.info("try to connect...")
        self.conn = self.engine.connect()
        self.logger.info("connecting is successful")

    def __del__(self):
        if self.conn is not None:
            self.conn.close()

    def __check_dialect(self):
        if self.db not in base_converter_params.keys():
            raise ModuleNotFoundError(
                "Dialect for {} type of database was'nt found, should be in list {}".format(
                    self.db, list(base_converter_params.keys())
                )
            )
        return True

    @property
    def meta(self):
        if "schema" in self.cred:
            meta = MetaData(bind=self.engine, schema=self.schema)
        else:
            meta = MetaData(bind=self.engine)
        if self.table_name is None:
            tables = self.tables
        else:
            tables = [self.table_name]
        if len(tables) > 0 and self.table_checker:
            try:
                meta.reflect(only=tables)
            except sqlalchemy.exc.InvalidRequestError:
                raise sqlalchemy.exc.InvalidRequestError(
                    "One or more file didn't find in database {}. Critical exception"
                )
        elif len(tables) > 0 and not self.table_checker:
            try:
                meta.reflect(only=tables)
            except sqlalchemy.exc.InvalidRequestError:
                self.logger.error(
                    "One or more file didn't find in database {}. Load table later".format(
                        self.db
                    )
                )
                meta = None
        else:
            meta.reflect()
        return meta

    @property
    def dialect(self):
        return base_converter_params[self.db]["dialect"]

    @property
    def quote_char(self):
        return base_converter_params[self.db]["quote"]

    @property
    def __str__(self):
        return "DataBaseWorker_{}".format(self.db)

    @property
    def __repr__(self):
        return "DataBaseWorker_{}".format(self.db)

    def check_if_table_availible(self, table):
        if len(self.tables) > 0 and table not in self.tables:
            raise ModuleNotFoundError(
                "Table_name to convert {} should be in list {} or set tables param to default".format(
                    table, self.tables
                )
            )
        return True

    def insert_vertica(self, table_name, data, schema=None, table_suffix=None):
        """
        custom insert for vertica using json
        :param table_suffix: change table to insert
        :param schema:  schema to uplaad
        :param table_name:
        :param data: data to insert
        :return: nothing
        """
        if self.db != "vertica":
            raise ModuleNotFoundError("Available only for vertica data source")
        cursor = self.engine.raw_connection().cursor()
        keys_data = list(data[0].keys())
        columns = self.get_columns(table_name)
        keys_to_remove = list(set(keys_data) - set(columns))
        keys_data = [key for key in keys_data if key in columns]
        for item in data:
            for key in keys_to_remove:
                if key in item:
                    del item[key]
        fields_json = [
            key
            for key in keys_data
            if key in columns and columns[key] in ("long varbinary", "blob")
        ]
        vertica_insert(
            cursor=cursor,
            target=(schema or self.schema) + "." + table_name + (table_suffix or ""),
            fields_json=fields_json,
            fields=keys_data,
            data=data,
        )

    def insert_merge_vertica(
            self,
            table_name,
            data,
            staging_schema=None,
            schema=None,
            staging_table_suffix=None,
            key_fields=None,
            filter_merge_fields=None,
    ):
        """
        Insert and update data in target table using temporary staging table, only for vertica
        :param filter_merge_fields:
        :param key_fields:
        :param table_name:
        :param data:
        :param staging_schema:
        :param schema:
        :param staging_table_suffix:
        :return: Nothing
        """
        if key_fields is None:
            key_fields = ["id"]
        if self.db != "vertica":
            raise ModuleNotFoundError("Available only for vertica data source")
        schema = schema or self.schema
        staging_table_name = "{staging_schema}.{table_name}{staging_table_suffix}".format(
            staging_schema=staging_schema,
            table_name=table_name,
            staging_table_suffix=staging_table_suffix or "",
        )
        sql_create_staging = "create table {staging_table_name} like {schema}.{table_name}".format(
            staging_table_name=staging_table_name, table_name=table_name, schema=schema
        )
        self.logger.info(sql_create_staging)
        self.conn.execute(sql_create_staging)
        try:
            self.insert_vertica(
                table_name,
                data,
                schema=staging_schema,
                table_suffix=staging_table_suffix,
            )
            self.logger.info(
                vertica_merge(
                    conn=self.conn,
                    table_name=schema + "." + table_name,
                    staging_table_name=staging_table_name,
                    fields=self.get_columns(table_name),
                    key_fields=key_fields,
                    filter_merge_fields=filter_merge_fields,
                )
            )
        finally:
            sql_drop = "drop table {staging_table_name} cascade".format(
                staging_table_name=staging_table_name
            )
            self.logger.info(sql_drop)
            self.conn.execute(sql_drop)

    def get_table_schema(self, table_name):
        columns_name = [
            "column_name",
            "data_type",
            "character_maximum_length",
            "column_default",
        ]
        self.table_name = table_name
        table_sql = Table(table_name, self.meta)
        self.table_name = None
        columns = [c.name for c in table_sql.columns]
        types = [get_type_sql_alchemy(c.type) for c in table_sql.columns]
        length = [get_length_type_sql_alchemy(c.type) for c in table_sql.columns]
        default = [get_default_arg_sql_alchemy(c) for c in table_sql.columns]
        fields = list(zip(columns, types, length, default))
        fields = [dict(zip(columns_name, f)) for f in fields]
        return fields

    def get_columns(self, table_name):
        """get column:type dict"""
        if self.check_if_table_availible(table_name):
            fields = self.get_table_schema(table_name)

        columns = [
            f["column_name"] for f in fields if f["column_name"] not in excluded_fields
        ]
        types = [
            f["data_type"] for f in fields if f["column_name"] not in excluded_fields
        ]
        return dict(zip(columns, types))
