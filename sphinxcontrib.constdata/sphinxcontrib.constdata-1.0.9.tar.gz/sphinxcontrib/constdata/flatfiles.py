"""
Flatfiles handling.

Important classes are:

* SqlCommand - easy executing SQL commands
* *FileToDb -- copy file to table (AbstractFileToDb, CsvFileToDb, JsonFileToDb, and AutodetectFileToDb)
* FlatfileReader --
"""

import csv
import json
import sqlite3
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Type, Union

import yaml
from sphinx.application import Sphinx
from sphinx.util import logging

from sphinxcontrib.constdata.settings import _CONN_ATTR, Settings
from sphinxcontrib.constdata.utils import ConstdataError

logger = logging.getLogger(__name__)

CACHEDB_FILENAME = "constdata.db"
"""Sqlite filename created under <outdir>/<builder>/"""


class SqlCommand:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.row_factory = sqlite3.Row

    def execute(self, sql: str, params: Mapping[str, str] = None) -> None:
        # Sqlite3: if None is passed to params in execute(sql, params) method,
        # it causes "ValueError: parameters are of unsupported type"
        # Psycopg2: None is okay
        self.conn.cursor().execute(sql, params or {})
        # Sqlite3: Python Sqlite3 module doesn't work in auto-commit (needs
        # explicit commit)
        self.conn.commit()

        # sqlite3: rowcount before actual fetching is -1, so we cant't help

    def select_one(self, sql: str, params: Mapping[str, str] = None) -> Dict[str, Any]:
        """
        Select exactly one row.

        IMPORTANT::

            exist = sql_command.select_one("select count(1) from foo")
            #                           or "select count(*) from foo" etc.
            bool(exist)

        will always be True, because response is { "count": 0 }, not None! Correct pattern is::

            exist = sql_command.select_one("select 1 from foo")
            #                          or  "select * from foo" etc.
            bool(exist)

        :raises ValueError: if more then one row would be returned
        :raises SyntaxError: if underlying database error has occured
        :return: Dict representing returned row or empty dict on no result.
        """
        rs = self._execute(sql, params)

        rs_len = len(rs)
        if rs_len == 0:
            return {}

        if rs_len > 1:
            raise ValueError(
                f"Expected to obtain exactly one row, but {rs_len} returned by query {sql}"
            )

        # Pick first (the only) row and make a dict from it
        row = rs[0]
        return self._row_to_dict(row)

    def select(
        self, sql: str, params: Mapping[str, Any] = None
    ) -> Sequence[Dict[str, Any]]:
        """
        Select multiple rows.

        :raises SyntaxError: if underlying database error has occured
        :return: Sequence of dicts or empty sequence if no rows.
        """
        rs = self._execute(sql, params)

        rt = [self._row_to_dict(r) for r in rs]
        return rt

    def make_create_table_sql(self, table_name: str, col_names: Sequence[str]) -> str:
        """Generate SQL with CREATE TABLE where all columns are text, the first one is PK."""
        # double quote identifiers
        col_names = [f'"{col}"' for col in col_names]
        # append column specs, the first one is PK
        col_specs = [f"{col} text" for col in col_names]
        col_specs[0] = f"{col_names[0]} text primary key not null"
        col_sql = ", ".join(col_specs)

        return f'create table "{table_name}" ({col_sql})'

    def make_insert_sql(self, table_name: str, new_row_dict: Mapping[str, str]) -> str:
        """Assemble parametrized "INSERT INTO" SQL from passed dict.

        For example for dict ``{"c1": "v1", "c2": "v2"}`` builds ``insert into "block" ("c1", "c2") values (%(c1)s, %(c2)s)``."""
        # double quote identifiers
        col_names = [f'"{col}"' for col in new_row_dict.keys()]
        # e.g. "c1", "c2"
        columns_sql = ", ".join(col_names)
        # e.g. :c1, :c2
        params_sql = ", ".join([f":{column}" for column in new_row_dict.keys()])
        insert_sql = f'insert into "{table_name}" ({columns_sql}) values ({params_sql})'

        return insert_sql

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Converts Sqlite3 Row to a dict"""
        return {k: row[k] for k in row.keys()}

    def _execute(self, sql, params) -> Sequence[sqlite3.Row]:
        """
        Execute and return, wrap any sqlite3 exception to SyntaxError

        :raises SyntaxError:
        """
        try:
            rs = self.conn.cursor().execute(sql, params or {}).fetchall()
        # any sqlite3 exception
        except sqlite3.Error as ex:
            raise ConstdataError(f"Cache DB error", orig_exc=ex)
        return rs


class AbstractFileToDb(metaclass=ABCMeta):
    """
    Abstract file to DB table class. It only knows how to save rows to DB, but children must implement file reading mechanism by overriding :py:meth:`run`.

    DB table name will be passed path (e.g. "path/to/menu.csv" is path and table name). Table will be re-created if it exists.
    """

    def __init__(self, settings: Settings, rel_path: Union[Path, str]):
        self.settings = settings
        # convert to Path if it is not already
        self.rel_path = Path(rel_path)
        self.sql_command = SqlCommand(settings.get_cachedb_conn())
        # for e.g. "path/to/menu.csv"
        self.table_name = str(rel_path)

    @abstractmethod
    def run(self):
        """
        Read a file and pass its rows to :py:meth:`save_rows_to_db`.
        """
        pass

    def save_rows_to_db(self, rows: Iterable[Sequence[str]]):
        """
        Save rows to a database table. Table is re-created if it exists.

        :param rows: list of lists, where sublist is a row fields. Including (the first) header row. E.g. two rows is ``[['h1', 'h2'], ['v1', 'v2']]``
        """
        for i, row in enumerate(rows):
            # row is a list of strings

            if i == 0:
                # first row contains column names
                header_row = row

                # if here, rows aren't empty, so drop and create table
                sql = f'drop table if exists "{self.table_name}"'
                self.sql_command.execute(sql)

                sql = self.sql_command.make_create_table_sql(
                    self.table_name, header_row
                )
                self.sql_command.execute(sql)

            else:
                # check header-row field mismatch
                row_len = len(row)
                header_row_len = len(header_row)
                assert (
                    row_len == header_row_len
                ), f"Corrupted file {self.rel_path}. Number of fields in the header is {header_row_len}, but the row {i+1} contains {row_len} fields."

                # insert into
                new_row_dict = {col: val for col, val in zip(header_row, row)}
                sql = self.sql_command.make_insert_sql(self.table_name, new_row_dict)
                self.sql_command.execute(sql, new_row_dict)

    def _list_of_dicts_to_list_of_lists(
        self, list_of_dicts: Sequence[Mapping]
    ) -> Iterable[Sequence[str]]:
        """
        Helper that takes a list of dicts [{},{}] and returns a list of lists as expected by :py:method:`save_rows_to_db`.
        """
        rows = []
        for i, row in enumerate(list_of_dicts):
            # each row is a dict with the keys as header
            if i == 0:
                header_row = [k for k in row.keys()]
                rows.append(header_row)

            next_row = [v for v in row.values()]
            rows.append(next_row)
        return rows


class CsvFileToDb(AbstractFileToDb):
    def run(self):
        abs_path = self.settings.get_root() / self.rel_path
        # csv module requires to open file with newline='' to correctly
        # interpret newlines inside values
        encoding = self.settings.get_files_encoding()
        fmtparams = self.settings.get_csv_fmt_params()
        with open(abs_path, newline="", encoding=encoding) as f:
            reader = csv.reader(f, **fmtparams)
            self.save_rows_to_db(reader)


class JsonFileToDb(AbstractFileToDb):
    def run(self):
        abs_path = self.settings.get_root() / self.rel_path
        encoding = self.settings.get_files_encoding()
        with open(abs_path, encoding=encoding) as f:
            # deserialize to list of dicts [{},{}]
            obj = json.load(f)

        rows = self._list_of_dicts_to_list_of_lists(obj)

        self.save_rows_to_db(rows)


class YamlFileToDb(AbstractFileToDb):
    def run(self):
        abs_path = self.settings.get_root() / self.rel_path
        encoding = self.settings.get_files_encoding()
        with open(abs_path, encoding=encoding) as f:
            # deserialize to list od dicts [{}, {}]
            obj = yaml.safe_load(f)

        rows = self._list_of_dicts_to_list_of_lists(obj)

        self.save_rows_to_db(rows)


class AutodetectFileToDb(AbstractFileToDb):
    """
    FileToDb class that autodetect file format from file extension and delegates a work on it.
    """

    def run(self):
        suffix = self.rel_path.suffix
        clazz: Optional[Type[AbstractFileToDb]] = None

        if suffix == ".csv":
            clazz = CsvFileToDb
        elif suffix == ".json":
            clazz = JsonFileToDb
        elif suffix == ".yaml" or suffix == ".yml":
            clazz = YamlFileToDb
        else:
            raise ValueError(
                f"File {self.rel_path} has unsupported file extension {suffix}"
            )

        clazz(self.settings, self.rel_path).run()


class FlatfileReader:
    """
    Read and query a flatfile. Despite its name, it actually lookup table in cachedb instead.
    """

    def __init__(self, settings: Settings, rel_path: Union[str, Path]):
        self.settings = settings
        self.rel_path = Path(rel_path)
        self.sql_command = SqlCommand(settings.get_cachedb_conn())

    def get_row_by_id(self, row_id: str) -> Dict[str, str]:
        """
        Return a row matching passed id as dict.
        """
        id_col_name = self.settings.get_id_col_name(self.rel_path)
        sql = f'select * from "{self.rel_path}" where "{id_col_name}" = :id'
        row = self.sql_command.select_one(sql, {"id": row_id})

        return row

    def iterate_rows(self, query: str = None) -> Sequence[Dict[str, Any]]:
        """Returns rows (as list of dicts) matching a query. Empty list on no matches or SyntaxError on underlying SQL error."""
        if not query:
            query = f'select * from "{self.rel_path}"'

        return self.sql_command.select(query)


def cache_flatfiles(app: Sphinx):
    """Create cachedb and cache all found flatfiles in root to a database. Called as Sphinx extension hook, thus app argument."""

    # open (create, if not exist) and share cachedb connection as Sphinx
    # attribute (app.outdir is e.g. _build/html for html builder)
    cachedb_path = Path(app.outdir, "constdata.db")
    setattr(app, _CONN_ATTR, sqlite3.connect(cachedb_path))

    assert app.env
    settings = Settings(app.env)
    root = settings.get_root()

    flatfiles = rglob_flatfiles_from(root)

    for abs_path in flatfiles:
        rel_path = abs_path.relative_to(root)
        AutodetectFileToDb(settings, rel_path).run()


def rglob_flatfiles_from(root: Path) -> List[Path]:
    """Gets list of supported flatfiles recurively found in passed folder"""
    flatfiles = (
        list(root.rglob("*.csv"))
        + list(root.rglob("*.json"))
        + list(root.rglob("*.yaml"))
        + list(root.rglob("*.yml"))
    )
    return flatfiles


def close_cachedb(app: Sphinx, ex: Exception):
    """build-finished hook properly closing cachedb connection"""
    getattr(app, _CONN_ATTR).close()
