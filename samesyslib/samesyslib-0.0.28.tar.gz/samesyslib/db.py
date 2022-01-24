import json
from functools import wraps
from time import time
import tempfile

from sqlalchemy import create_engine, engine
import pandas as pd

import logging

log = logging.getLogger(__name__)
# no log by default unless log system gets configured in the main code
log.addHandler(logging.NullHandler())


def timing(f):
    """
    add documentation here

    Examples:
        add examples
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        verbose = False
        if kwargs is not None:
            if "timing_verbose" in kwargs.keys():
                verbose = kwargs["timing_verbose"]
        start = time()
        result = f(*args, **kwargs)
        end = time()
        if verbose:
            log.info(f"Function: {f.__name__}.\
                Elapsed time: {round(end - start, 1)} s")
        return result

    return wrapper


class POptimiseDataTypesMixin:
    def mem_usage(self, pandas_obj: pd.DataFrame, **kwargs: dict) -> str:
        if isinstance(pandas_obj, pd.DataFrame):
            usage_b = pandas_obj.memory_usage(deep=True).sum()
        else:  # we assume if not a df it's a series
            usage_b = pandas_obj.memory_usage(deep=True)
        usage_mb = usage_b / 1024 ** 2  # convert bytes to megabytes
        return "{:03.2f} MB".format(usage_mb)

    @timing
    def optimize_pandas_datatypes(
        self, data: pd.DataFrame, **kwargs: dict
    ) -> pd.DataFrame:
        verbose = False
        if kwargs is not None:
            if "optimize_verbose" in kwargs.keys():
                verbose = kwargs["optimize_verbose"]
        if verbose:
            log.info("OPTIMIZING PANDAS DATAFRAMES DATATYPES")
        memory_before = self.mem_usage(data)
        result = data.select_dtypes(include=["int"]).apply(
            pd.to_numeric, downcast="unsigned"
        )
        data[result.columns] = result

        result = data.select_dtypes(include=["float"]).apply(
            pd.to_numeric, downcast="float"
        )
        data[result.columns] = result

        if verbose:
            log.info(
                "RAM usage before/after optimization: {} / {}".format(
                    memory_before, self.mem_usage(data)
                )
            )
        return data


class DB(POptimiseDataTypesMixin):
    def __init__(self, connection_parms, conn=None, if_pymysql=False, if_mysqldb=False):
        """inputs:
            if_mysqldb - should we use mysqlclient (fork of MySQL-Python) driver? Supposed to be the fastest connection.
            if_pymysql - should we use pymysql (purely python based) driver? Well supported and maintained.
            if both if_mysqldb and if_pymysql are set to True, if_mysqldb takes priority
        """
        if type(conn) is engine.Engine:
            self.engine = conn
        else:
            if type(connection_parms) is dict:
                self.params = connection_parms
            else:
                self.params = json.loads(connection_parms)

            if not self.params:
                raise Exception("DB connection params not provided")

            if if_mysqldb:
                connector = "+mysqldb" 
            elif if_pymysql:
                connector = "+pymysql" 
            else:
                connector = ""

            self.engine = create_engine(
                f"mysql{connector}://{self.params['login']}:"
                f"{self.params['password']}@"
                f"{self.params['host']}"
                f":{self.params['port']}/"
                f"{self.params['schema']}?charset=utf8mb4&local_infile=1",
                pool_pre_ping=True,
            )
        self._check_local_infile()

    def _check_local_infile(self):
        SQL = "SHOW GLOBAL VARIABLES LIKE 'local_infile';"
        result = self.engine.execute(SQL).fetchone()
        assert result[0] == "local_infile", "Check For local_infile value"
        assert result[1] == "ON", "[CL ERROR] local_infile value IS OFF"

    @timing
    def get(self, query: str = None, **kwargs: dict) -> pd.DataFrame:
        verbose = False
        if kwargs is not None:
            if "verbose" in kwargs.keys():
                verbose = kwargs["verbose"]
        if verbose:
            log.info(f"Executing query:\n{query}")
        df = self.optimize_pandas_datatypes(
            pd.read_sql_query(query, self.engine), **kwargs
        )
        if verbose:
            log.info(f"Returned table shape: {df.shape}")
        return df

    @timing
    def send_single(
        self,
        pdf: pd.DataFrame,
        table: str = None,
        chunksize: int = 10000,
        schema: str = None,
        if_exists: str = "replace",
        index: bool = False,
        method: str = "multi",
        **kwargs: dict,
    ) -> pd.DataFrame:
        try:
            pdf.to_sql(
                table,
                self.engine,
                chunksize=chunksize,
                if_exists=if_exists,
                schema=schema,
                index=index,
                method=method,
            )
        except Exception as e:
            log.error("SQL EXCEPTION: {}".format(str(e)))
        return table

    @timing
    def execute(self, sql: str, **kwargs: dict):
        verbose = False
        if kwargs is not None:
            if "verbose" in kwargs.keys():
                verbose = kwargs["verbose"]

        if verbose:
            log.info(f"""Executing query:\n{sql}""")

        result = self.engine.execute(sql)
        if verbose:
            log.info(f"Inserted rows:{result.rowcount}")

        return result

    @timing
    def run(self, sql, **kwargs):
        with self.engine.begin() as conn:
            conn.execute(sql)

    @timing
    def send_append(
        self, pdf: pd.DataFrame, table: str = None, schema: str = None, **kwargs
    ) -> str:
        verbose = False
        if kwargs is not None:
            if "verbose" in kwargs.keys():
                verbose = kwargs["verbose"]

        table_name = table
        if schema is None:
            schema = self.params["schema"]

        try:
            with self.engine.connect() as conn:
                conn.execute(f"USE {schema}")

                if not conn.execute(f'show tables like "{table_name}"'):
                    create_stmt = pd.io.sql.get_schema(pdf, table_name, con=self.engine)
                    if verbose:
                        log.info(f"Executing query:\n{create_stmt}")
                    conn.execute(create_stmt)

                with tempfile.NamedTemporaryFile() as tf:
                    pdf.to_csv(
                        tf.name,
                        encoding="utf-8",
                        header=True,
                        doublequote=True,
                        sep=",",
                        index=False,
                        na_rep="NULL",
                    )

                    load_stmt = f"""
                    LOAD DATA LOCAL INFILE '{tf.name}'
                    INTO TABLE {schema}.{table_name} FIELDS TERMINATED BY ',' ENCLOSED BY '\"'
                    IGNORE 1 LINES;
                    """
                    if verbose:
                        log.info(f"Executing query:\n{load_stmt}")
                    rows = conn.execute(load_stmt)

        except Exception as e:
            log.error(f"SQL EXCEPTION: {str(e)}")

        return f"{schema}.{table}"

    @timing
    def send(
        self,
        pdf: pd.DataFrame,
        table: str = None,
        schema: str = None,
        if_exists: str = "replace",
        index: bool = False,
        **kwargs: dict,
    ) -> str:
        if if_exists != "replace":
            return self.send_append(
                pdf, table=table, if_exists=if_exists, index=index, **kwargs
            )

        verbose = False
        if kwargs is not None:
            if "verbose" in kwargs.keys():
                verbose = kwargs["verbose"]

        tmp_prefix = "_tmp"
        if schema is None:
            schema = self.params["schema"]

        try:
            with self.engine.connect() as conn:
                query = f"DROP TABLE IF EXISTS {schema}.{table}, {schema}.{table + tmp_prefix};"
                if verbose:
                    log.info(f"Executing query:\n{query}")
                conn.execute(query)
                with tempfile.NamedTemporaryFile() as tf:
                    pdf.to_csv(
                        tf.name,
                        encoding="utf-8",
                        header=True,
                        chunksize=300000,
                        doublequote=True,
                        sep=",",
                        index=False,
                        na_rep="NULL",
                    )
                    conn.execute(f"USE {schema};")
                    create_stmt = pd.io.sql.get_schema(
                        pdf, table + tmp_prefix, con=self.engine
                    )
                    if verbose:
                        log.info(f"Executing query:\n{create_stmt}")
                    conn.execute(create_stmt)

                    load_stmt = f"""
                    LOAD DATA LOCAL INFILE '{tf.name}'
                    INTO TABLE {schema}.{table+tmp_prefix}
                    FIELDS TERMINATED BY ',' ENCLOSED BY '\"' IGNORE 1 LINES;
                    """
                    if verbose:
                        log.info(f"Executing query:\n{load_stmt}")
                    rows = conn.execute(load_stmt)
                    conn.execute(
                        f"RENAME TABLE {schema}.{table + tmp_prefix} TO {schema}.{table};"
                    )
            log.info(
                f"Successfully loaded csv into table {schema}.{table} {rows.rowcount} rows."
            )

        except Exception as e:
            log.error(f"SQL EXCEPTION: {str(e)}")

        return f"{schema}.{table}"


    def size(self, schema: str = None) -> pd.DataFrame:
        """Create a dataframe of sizes of tables"""
        if schema:
            condition = f'''TABLE_SCHEMA = "{schema}"'''
        else:
            condition = "TRUE"
        query = f"""SELECT
                    TABLE_SCHEMA as `Database`,
                    TABLE_NAME AS `Table`,
                    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024) AS `Size_MB`
                    FROM
                    information_schema.TABLES
                    WHERE
                    {condition}
                    ORDER BY
                    TABLE_SCHEMA, (DATA_LENGTH + INDEX_LENGTH)
                    DESC;
                    """
        try:
            df= pd.read_sql_query(query, self.engine)
            return df
        except Exception as e:
            log.error(f"SQL EXCEPTION: {str(e)}")


    def create_on_statement(self):
        on = " AND ".join([f"s.{id_col} = t.{id_col}" for id_col in self.id_cols])
        return on

    def create_update_statement(self):
        update = ", ".join(
            [f"t.{col} = s.{col}" for col in self.columns if col not in self.id_cols]
        )
        return update

    def create_insert_statement(self):
        insert = f"({', '.join(self.columns)})"

        values = ", ".join([f"s.{col}" for col in self.columns])
        values = f"({values})"

        return insert, values


    @timing
    def upsert(
        self,
        pdf: pd.DataFrame,
        table: str = None,
        chunksize: int = 10000,
        schema: str = None,
        if_exists: str = "replace",
        index: bool = False,
        method: str = "multi",
        **kwargs: dict,
    ) -> pd.DataFrame:
        try:
            pdf.to_sql(
                table,
                self.engine,
                chunksize=chunksize,
                if_exists=if_exists,
                schema=schema,
                index=index,
                method=method,
            )
        except Exception as e:
            log.error("SQL EXCEPTION: {}".format(str(e)))
        return table