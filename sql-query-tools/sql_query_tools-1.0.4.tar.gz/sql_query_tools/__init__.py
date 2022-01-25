"""Top-level package for SQL Query Tools."""

from . import _version
__version__ = _version.get_versions()['version']


__author__ = """Andoni Sooklaris"""
__email__ = 'andoni.sooklaris@gmail.com'

import csv
import logging
import os
import pandas as pd
import pathlib
import sqlalchemy
import typing
from tqdm import tqdm
from .utils import logger_setup, assert_value_dtype, ensurelist, systime, find_binary, syscmd, listfiles


logger = logger_setup(name='sql-query-tools', level=logging.WARNING)


class Postgres(object):
    """
    Manage interaction with Postgres database via SQLAlchemy. Begin by passing the credentials
    to your Postgres database either through the enumerated arguments of this class, or
    by storing those credentials in a .pgpass file in standard format:

        hostname,port,db_name,user_name,password

    and passing the path to that file to the `credentials_fpath` argument.
    """
    def __init__(self,
                 hostname: str=None,
                 port: str=None,
                 db_name: str=None,
                 pg_user: str=None,
                 pw: str=None,
                 credentials_fpath: str=os.path.expanduser('~/.pgpass')) -> None:
        # Get credentials
        credentials_fpath = os.path.expanduser(credentials_fpath)
        if os.path.isfile(credentials_fpath):
            self.hostname, self.port, self.db_name, self.pg_user, self.pw = self.read_pgpass(credentials_fpath)
        else:
            self.hostname = hostname
            self.port = port
            self.db_name = db_name
            self.pg_user = pg_user
            self.pw = pw

        assert self.hostname is not None, 'Must provide hostname'
        assert self.port is not None, 'Must provide port'
        assert self.db_name is not None, 'Must provide database name'
        assert self.pg_user is not None, 'Must provide username'
        assert self.pw is not None, 'Must provide password'

        self.dbcon = self.connect()

        self.null_equivalents = ['nan', 'n/a', 'null', 'none', '']
        self.null_equivalents = self.null_equivalents + [x.upper() for x in self.null_equivalents]

    def read_pgpass(self, credentials_fpath: str) -> tuple:
        """
        Read ~/.pgpass file if it exists and extract Postgres credentials. Return tuple
        in format: `hostname, port, db_name, user_name, password`
        """
        with open(os.path.expanduser(credentials_fpath), 'r') as f:
            pgpass_contents = f.read().split(':')

        # Ensure proper pgpass format, should be a tuple of length 5
        assert len(pgpass_contents) == 5, \
            'Invalid ~/.pgpass contents format. Should be `hostname:port:db_name:user_name:password`'

        return tuple(pgpass_contents)

    def connect(self) -> sqlalchemy.engine.base.Connection:
        """
        Connect to Postgres database and return the database connection.
        """
        con_str = f'postgresql://{self.pg_user}@{self.hostname}:{self.port}/{self.db_name}'
        return sqlalchemy.create_engine(con_str)

    def execute(self,
                sql: str,
                logfile: typing.Union[str, pathlib.Path]=None,
                progress: bool=False) -> None:
        """
        Execute a SQL string or a list of SQL statements. Optionally control the logging of
        each individual SQL statement executed to a local log textfile with the `logfile`
        parameter.
        """
        write_log = False if logfile is None else True
        if write_log:
            logger.info(f'Writing SQL query log to file "{logfile}"')

        sql = ensurelist(sql)

        with self.dbcon.begin() as con:
            if progress:
                pbar = tqdm(total=len(sql), unit='query')

            for stmt in sql:
                con.execute(sqlalchemy.text(stmt))

                if write_log:
                    with open(logfile, 'a') as f:
                        entry = stmt + '\n'
                        entry = systime(as_string=True) + ' ' + entry  # Prepend timestamp
                        f.write(entry)

                if progress:
                    pbar.update(1)

        if progress:
            pbar.close()

    def read_sql(self, sql: str, simplify: bool=True) -> typing.Union[pd.Series, pd.DataFrame]:
        """
        Execute SQL and read results using Pandas, optionally simplify result to a Series if
        the result is a single-column dataframe.
        """
        res = pd.read_sql(sql, con=self.dbcon)

        if res.shape[1] == 1:
            if simplify:
                logger.info(f'Simplifying result data to pd.Series, length: {str(len(res))}')
                res = res.iloc[:, 0]

        return res

    def get_table_name(self, schema_name: str=None, table_name: str=None) -> str:
        """
        Concatenate a schema and table names. Require that `table_name` is supplied,
        but `schema_name` may be blank (i.e. in the case of querying pg_stat, or another
        builtin table that does not have an explicit corresponding schema.)
        """
        assert table_name is not None, 'Must supply `table_name`'

        if schema_name is None:
            return table_name
        else:
            return schema_name + '.' + table_name

    def validate_dtype(self, schema_name: str, table_name: str, col: str, val: typing.Any) -> bool:
        """
        Query database for datatype of value and validate that the Python value to
        insert to that column is compatible with the SQL datatype.
        """
        if table_name.startswith('pg_'):
            # Builtin table housed in `pg_catalog` schema, but no schema required to query from it
            schema_name = 'pg_catalog'

        table_schema_and_name = self.get_table_name(schema_name, table_name)
        full_col = table_schema_and_name + '.' + col

        infoschema = self.infoschema(infoschema_table='columns')[['table_schema', 'table_name', 'column_name', 'data_type', 'is_nullable']]
        infoschema = infoschema.loc[
            (infoschema['table_schema']==schema_name)
            & (infoschema['table_name']==table_name)
            & (infoschema['column_name']==col)
        ]

        assert len(infoschema), f'Nonexistent column {full_col}'
        infoschema = infoschema.squeeze().to_dict()

        if val == 'NULL' or val is None:
            if bool(infoschema['is_nullable']) is True:
                return True
            else:
                logger.error(f"Value 'NULL' (dtype: {val.__class__.__name__}) not allowed for column {full_col}")
                return False

        # Check that input value datatype matches queried table column datatype
        dtype = self.col_dtypes(schema_name, table_name)[col]
        dtype_map = {
            'bigint': 'int',
            'int8': 'int',
            'bigserial': 'int',
            'serial8': 'int',
            'integer': 'int',
            'int': 'int',
            'int4': 'int',
            'smallint': 'int',
            'int2': 'int',
            'double precision': 'float',
            'float': 'float',
            'float4': 'float',
            'float8': 'float',
            'numeric': 'float',
            'decimal': 'float',
            'character': 'str',
            'char': 'str',
            'character varying': 'str',
            'varchar': 'str',
            'text': 'str',
            'date': 'str',
            'timestamp': 'str',
            'timestamp with time zone': 'str',
            'timestamp without time zone': 'str',
            'name': 'str',
            'boolean': 'bool',
            'bool': 'bool',
        }

        # Get python equivalent of SQL column datatype according to dtype_map above
        python_dtype = [v for k, v in dtype_map.items() if dtype in k]

        if not len(python_dtype):
            known_python_datatypes = list(set([v for k, v in dtype_map.items()]))
            logger.error(f"""
            Unable to match SQL column '{full_col}' datatype {dtype} to any known Python
            datatypes {known_python_datatypes}""")
            return False
        else:
            python_dtype = python_dtype[0]

        true_python_dtype = type(val).__name__

        # Prepare message to be used in event of incompatible datatypes
        msg = f"""Incompatible datatypes! SQL column {full_col} has type
        `{dtype}`, and Python value `{str(val)}` is of type `{val.__class__.__name__}`."""

        # Begin validation
        if true_python_dtype in ['date', 'datetime']:
            if 'date' in dtype or 'timestamp' in dtype:
                return True
            else:
                return False

        elif python_dtype == 'bool':
            if isinstance(val, bool):
                return True
            else:
                if isinstance(val, str):
                    if val.lower() in ['t', 'true', 'f', 'false']:
                        return True

        elif python_dtype == 'int':
            if isinstance(val, int):
                return True
            else:
                if isinstance(val, str):
                    try:
                        int(val)
                        return True
                    except:
                        pass

        elif python_dtype == 'float':
            if isinstance(val, float):
                return True
            else:
                if val == 'inf':
                    pass
                try:
                    float(val)
                    return True
                except:
                    pass

        elif python_dtype == 'str':
            if isinstance(val, str):
                return True
        else:
            return True

        # If this function hasn't returned True by now, then datatype validation must have failed
        logger.debug(msg)
        return False

    def infoschema(self, infoschema_table: str) -> pd.DataFrame:
        """
        Query from information_schema. Vanilla call to this function executes:

            select * from information_schema.{columns_or_tables};

        Can also set `infoschema_table` to "tables", or any other subdivision of Postgres'
        information schema.
        """
        sql = f'select *\nfrom information_schema.{infoschema_table}'
        df = self.read_sql(sql, simplify=False)
        logger.info(f'Retrieved information_schema.{infoschema_table}')

        # Format known column datatypes
        bool_cols = ['is_nullable']
        for bcol in bool_cols:
            if bcol in df.columns:
                df[bcol] = df[bcol].map(lambda x: dict(YES=True, NO=False)[x])

        return df

    def build_update(self,
                     schema_name,
                     table_name,
                     pkey_name,
                     pkey_value,
                     columns,
                     values,
                     validate=True,
                     newlines=False) -> str:
        """
        Construct a SQL UPDATE statement.

        By default, this method will:

            - Attempt to coerce a date value to proper format if the input value is detect_dtype
              as a date but possibly in the improper format. Ex: '2019:02:08' -> '2019-02-08'
            - Quote all values passed in as strings. This will include string values that
              are coercible to numerics. Ex: '5', '7.5'.
            - Do not quote all values passed in as integer or boolean values.
            - Primary key value is quoted if passed in as a string. Otherwise, not quoted.

        schema {str} name of schema
        table {str} SQL table name
        pkey_name {str} name of primary key in table
        pkey_value {str} value of primary key for value to update
        columns {list} columns to consider in UPDATE statement
        values {list} values to consider in UPDATE statement
        validate {bool} validate that each value may be inserted to destination column
        newlines {true} add newlines to query string to make more human-readable
        """
        columns = ensurelist(columns)
        values = ensurelist(values)
        if len(columns) != len(values):
            raise Exception("Parameters `columns` and `values` must be of equal length")

        pkey_value = self._single_quote(pkey_value)
        lst = []

        for col, val in zip(columns, values):
            if validate:
                test = self.validate_dtype(schema_name, table_name, col, val)
                if not test:
                    dtype = type(val).__name__
                    raise Exception(f'Dtype mismatch. Value: {val}, dtype: {dtype}, column: {col}')

            if str(val).lower() in self.null_equivalents:
                val = 'NULL'
            elif assert_value_dtype(val, 'bool') or assert_value_dtype(val, 'int') or assert_value_dtype(val, 'float'):
                pass
            else:
                # Assume string
                val = self._single_quote(val)

            if newlines:
                lst.append(f'\n    "{col}"={str(val)}')
            else:
                lst.append(f'"{col}"={str(val)}')

        sql = ["UPDATE {}", "SET {}", "WHERE {} = {}"]
        if newlines:
            lst[0] = lst[0].strip()
            sql = '\n'.join(sql)
        else:
            sql = ' '.join(sql)

        table_schema_and_name = self.get_table_name(schema_name, table_name)
        return sql.format(table_schema_and_name,
                          ', '.join(lst),
                          '"' + pkey_name + '"',
                          pkey_value)

    def build_insert(self,
                     schema_name: str,
                     table_name: str,
                     columns: list,
                     values: list,
                     validate: bool=False,
                     newlines: bool=False) -> str:
        """
        Construct SQL INSERT statement.
        By default, this method will:

            - Attempt to coerce a date value to proper format if the input value is
              detect_dtype as a date but possibly in the improper format.
              Ex: '2019:02:08' -> '2019-02-08'
            - Quote all values passed in as strings. This will include string values
              that are coercible to numerics. Ex: '5', '7.5'.
            - Do not quote all values passed in as integer or boolean values.
            - Primary key value is quoted if passed in as a string. Otherwise, not quoted.

        schema {str} name of schema
        table {str} SQL table name
        columns {list} columns to consider in UPDATE statement
        values {list} values to consider in UPDATE statement
        validate {bool} validate that each value may be inserted to destination column
        newlines {true} add newlines to query string to make more human-readable
        """
        columns = ensurelist(columns)
        values = ensurelist(values)
        if len(columns) != len(values):
            raise Exception("Parameters `columns` and `values` must be of equal length")

        lst = []
        for col, val in zip(columns, values):
            if validate:
                test = self.validate_dtype(schema_name, table_name, col, val)
                if not test:
                    dtype = type(val).__name__
                    raise Exception(f"""Value '{val}' (dtype: {dtype})
                    is incompatible with column '{col}' """)

            if str(val).lower() in self.null_equivalents:
                val = 'null'

            elif assert_value_dtype(val, 'bool') or assert_value_dtype(val, 'int') or assert_value_dtype(val, 'float'):
                pass
            else:
                # Assume string, handle quotes
                val = self._single_quote(val)

            lst.append(val)

        values_final = ', '.join(str(x) for x in lst)
        values_final = values_final.replace("'null'", 'null')
        columns = ', '.join(['"' + x + '"' for x in columns])

        table_schema_and_name = self.get_table_name(schema_name, table_name)
        sql = ['insert into {table_schema_and_name} ({columns})', 'values ({values_final})']
        sql = '\n'.join(sql) if newlines else ' '.join(sql)

        return sql.format(**locals())

    def build_delete(self,
                     schema_name: str,
                     table_name: str,
                     pkey_name: str,
                     pkey_value: typing.Any,
                     newlines: bool=False) -> str:
        """
        Construct SQL DELETE FROM statement.
        """
        table_schema_and_name = self.get_table_name(schema_name, table_name)

        if isinstance(pkey_value, list):
            pkey_value_lst = [self._single_quote(x) for x in pkey_value]
            sql = ['delete from {}', 'where {} in ({})']
            pkey_value_str = ', '.join([str(x) for x in pkey_value_lst])
        else:
            pkey_value_str = self._single_quote(pkey_value)
            sql = ['delete from {}', 'where {} = {}']

        sql = '\n'.join(sql) if newlines else ' '.join(sql)
        return sql.format(table_schema_and_name, pkey_name, pkey_value_str)

    def col_names(self, schema_name: str, table_name: str) -> list:
        """
        Get column names of table as a list.
        """
        df_cols = self.infoschema(infoschema_table='columns')[['table_schema', 'table_name', 'column_name']]

        df_cols = df_cols.loc[(df_cols['table_schema'] == schema_name)
                              & (df_cols['table_name'] == table_name)]

        cols = df_cols['column_name'].tolist()
        return cols

    def col_dtypes(self, schema_name: str, table_name: str) -> int:
        """
        Get column datatypes of table as a dictionary.
        """
        infoschema = self.infoschema(infoschema_table='columns')
        infoschema = infoschema.loc[
            (infoschema['table_schema']==schema_name)
            & (infoschema['table_name']==table_name)
        ]
        return infoschema.set_index('column_name')['data_type'].to_dict()

    def read_table(self, schema_name: str, table_name: str) -> pd.DataFrame:
        """
        Read an entire SQL table or view as a dataframe.
        """
        df = self.read_sql(f'select * from "{schema_name}"."{table_name}"')
        logger.info(f"Read dataframe {schema_name}.{table_name}, shape: {df.shape}")
        return df

    def dump(self, backup_dir: typing.Union[str, pathlib.Path])-> str:
        """
        Wrap `pg_dump` and save an entire database contents to a directory.
        """
        backup_dir = os.path.expanduser(backup_dir)
        logger.info(f'Dumping database {self.db_name} to "{backup_dir}"')

        bin = find_binary('pg_dump', abort=True)
        output_fpath = f'{backup_dir}/{self.db_name}.sql'
        cmd = f'{bin} --user {self.pg_user} {self.db_name} > "{output_fpath}"'

        out = syscmd(cmd, encoding='utf-8')
        if not isinstance(out, int):
            if 'FATAL' in out:
                raise Exception(out.strip())

        return output_fpath

    def dump_tables(self, backup_dir: typing.Union[str, pathlib.Path], sep: str=',', coerce_csv: bool=False):
        """
        Dump each table in database to a textfile with specified separator.

        Source: https://stackoverflow.com/questions/17463299/export-database-into-csv-file?answertab=oldest#tab-top
        """
        db_to_csv = """
        CREATE OR REPLACE FUNCTION db_to_csv(path TEXT) RETURNS void AS $$
        DECLARE
           tables RECORD;
           statement TEXT;
        BEGIN
        FOR tables IN
           SELECT ('"' || table_schema || '"' || '.' || '"' || table_name || '"') AS schema_table
           FROM information_schema.tables t
               INNER JOIN information_schema.schemata s ON s.schema_name = t.table_schema
           WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema')
               AND t.table_type NOT IN ('VIEW')
           ORDER BY schema_table
        LOOP
           statement := 'COPY ' || tables.schema_table || ' TO ''' || path || '/' || replace(tables.schema_table, '"', '') || '.csv' ||''' DELIMITER ''{sep}'' CSV HEADER';
           EXECUTE statement;
        END LOOP;
        RETURN;
        END;
        $$ LANGUAGE plpgsql;""".format(**locals())
        self.execute(db_to_csv)

        # Execute function, dumping each table to a textfile.
        # Function is used as follows: SELECT db_to_csv('/path/to/dump/destination');
        logger.info(f'Dumping database {self.db_name} to "{backup_dir}" as tables stored as textfiles')
        self.execute(f"select db_to_csv('{backup_dir}')")

        # If coerce_csv is True, read in each file outputted, then write as a quoted CSV.
        # Replace 'sep' if different from ',' and quote each text field.
        if coerce_csv:
            if sep != ',':
                owd = os.getcwd()
                os.chdir(backup_dir)

                # Get tables that were dumped and build filenames
                get_dumped_tables = """
                select (table_schema || '.' || table_name) as schema_table
                from information_schema.tables t
                join information_schema.schemata s
                  on s.schema_name = t.table_schema
                where t.table_schema not in ('pg_catalog', 'information_schema')
                  and t.table_type not in ('VIEW')
                order by schema_table"""
                dumped_tables = self.read_sql(get_dumped_tables).squeeze()

                if isinstance(dumped_tables, pd.Series):
                    dumped_tables = dumped_tables.tolist()
                elif isinstance(dumped_tables, str):
                    dumped_tables = [dumped_tables]

                dumped_tables = [x + '.csv' for x in dumped_tables]

                # Read in each table and overwrite file with comma sep and quoted text values
                for csvfile in dumped_tables:
                    pd.read_csv(csvfile, sep=sep).to_csv(
                        csvfile, quoting=csv.QUOTE_NONNUMERIC, index=False)

                os.chdir(owd)
            else:
                logger.warning('`coerce_csv` is True but desired `sep` is not a comma!')

        # Get tables that were just dumped and return their filenames
        dumped_files_tmpcsv = listfiles(path=backup_dir, ext='tmpcsv', full_names=True)
        dumped_files = []
        for tmpcsvfile in dumped_files_tmpcsv:
            newfilename = os.path.splitext(tmpcsvfile)[0] + '.csv'
            os.rename(tmpcsvfile, newfilename)
            dumped_files.append(newfilename)

        return dumped_files

    def create_schema(self, schema_name: str) -> None:
        """
        Create a Postgres schema.
        """
        self.execute(f'create schema {schema_name}')

    def drop_schema(self, schema_name: str, if_exists: bool=False, cascade: bool=False) -> None:
        """
        Drop a Postgres schema with options to only drop if it currently exists, and
        to drop dependent objects on it with `cascade`.
        """
        cascade_str = ' cascade' if cascade else ''
        if_exists_str = 'if exists ' if if_exists else ''
        self.execute(f'drop schema {if_exists_str}{schema_name}{cascade_str}')

    def drop_schema_and_recreate(self, schema_name: str, if_exists: bool=False, cascade: bool=False) -> None:
        """
        Drop then re-create a Postgres schema
        """
        args = dict(schema_name=schema_name, if_exists=if_exists, cascade=cascade)
        self.drop_schema(**args)
        self.create_schema(schema_name)

    def list_tables(self, schema_name: str=None) -> pd.DataFrame:
        """
        Query information schema for a list of tables present in the database connection.
        """
        additional_cond = f"and table_schema = '{schema_name}'" if isinstance(schema_name, str) else ''
        sql = f"""
        select table_schema, "table_name"
        from information_schema.tables
        where table_type = 'BASE TABLE'
          {additional_cond}
        """
        return self.read_sql(sql)

    def table_exists(self, schema_name: str=None, table_name: str=None) -> bool:
        """
        Return a boolean indicating whether a table is existent in the database connection
        """
        tables = self.list_tables(schema_name)
        return table_name in tables['table_name'].tolist()

    def create_table(self, schema_name: str, table_name: str, columnspec: dict, if_not_exists: bool=False):
        """
        Create a Postgres table given a schema name, table name and column specification. The
        specification must be in format:

            {
                col1_name:col1_dtype,
                col2_name:col2_dtype,
                ...
            }
        """
        tab_ws = '    '

        columnspec_lst = []
        for col, dtype in columnspec.items():
            line_item = col + ' ' + dtype + ',\n'
            columnspec_lst.append(line_item)

        columnspec_str = tab_ws + tab_ws.join(columnspec_lst).rstrip('\n,')

        if_not_exists_str = 'if not exists ' if if_not_exists else ''
        create_table_sql_lst = [
            f'create table {if_not_exists_str}{schema_name}.{table_name} (',
            columnspec_str,
            ')',
        ]

        create_table_sql = '\n'.join(create_table_sql_lst)
        self.execute(create_table_sql)

    def wipe_table(self, schema_name: str, table_name: str) -> None:
        """
        Delete all records in a table but do not drop the table.
        """
        if self.table_exists(schema_name, table_name):
            self.execute(f'delete from {schema_name}.{table_name} where 1 = 1')

    def drop_table(self, schema_name: str, table_name: str, if_exists: bool=False, cascade: bool=False) -> None:
        """
        Drop a Postgres table.
        """
        if_exists_str = 'if exists ' if if_exists else ''
        cascade_str = ' cascade' if cascade else ''
        sql = f'drop table {if_exists_str}"{schema_name}"."{table_name}"{cascade_str}'
        self.execute(sql)

    def list_views(self, schema_name: str=None) -> pd.DataFrame:
        """
        Query information schema for a list of views present in the database connection.
        """
        where_clause = f"where table_schema = '{schema_name}'" if isinstance(schema_name, str) else ''
        sql = f"""
        select table_schema as view_schema, "table_name" as view_name
        from information_schema.views
        {where_clause}
        order by table_schema, view_name
        """
        return self.read_sql(sql)

    def view_exists(self, schema_name: str=None, view_name: str=None) -> bool:
        """
        Return a boolean indicating whether a view is existent in the database connection
        """
        views = self.list_views(schema_name)
        return view_name in views['view_name'].tolist()

    def table_or_view_exists(self, schema_name: str=None, table_or_view_name: str=None) -> bool:
        """
        Determine whether a table or view exists in the database connection.
        """
        return self.table_exists(schema_name, table_or_view_name) or self.view_exists(schema_name, table_or_view_name)

    def create_view(self, schema_name: str, view_name: str, view_sql: str, or_replace: bool=False):
        """
        Create a view from user-passed SQL.
        """
        or_replace_str = 'or replace ' if or_replace else ''
        sql = f'create {or_replace_str}view "{schema_name}"."{view_name}" as ({view_sql})'
        self.execute(sql)

    def drop_view(self, schema_name: str, view_name: str, if_exists: bool=False, cascade: bool=False) -> None:
        """
        Drop a Postgres view.
        """
        if_exists_str = 'if exists ' if if_exists else ''
        cascade_str = ' cascade' if cascade else ''
        sql = f'drop view {if_exists_str}"{schema_name}"."{view_name}"{cascade_str}'
        self.execute(sql)

    def trigger_exists(self, trigger_schema: str=None, trigger_name: str=None) -> bool:
        """
        Return a boolean indicating whether a trigger is existent in the database connection
        """
        triggers = self.list_triggers(trigger_schema)
        return trigger_name in triggers['trigger_name'].tolist()

    def list_triggers(self, trigger_schema: str=None) -> list:
        """
        Query information schema for a list of triggers present in the database connection.
        """
        where_clause = f"where trigger_schema = '{trigger_schema}'" if isinstance(trigger_schema, str) else ''
        sql = f"""
        select event_object_schema as table_schema
               , event_object_table as "table_name"
               , trigger_schema
               , trigger_name
               , string_agg(event_manipulation, ',') as "event"
               , action_timing as activation
               , action_condition as "condition"
               , action_statement as definition
        from information_schema.triggers
        {where_clause}
        group by 1, 2, 3, 4, 6, 7, 8
        order by table_schema, "table_name"
        """
        return self.read_sql(sql)

    def _single_quote(self, val: typing.Any):
        """
        Escape single quotes and put single quotes around value if string value.
        """
        if type(val) not in [bool, int, float]:
            val = str(val).replace("'", "''")
            val = "'" + val + "'"

        return val
