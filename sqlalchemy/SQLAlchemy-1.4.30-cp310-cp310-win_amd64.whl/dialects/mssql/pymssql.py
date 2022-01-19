# mssql/pymssql.py
# Copyright (C) 2005-2022 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

"""
.. dialect:: mssql+pymssql
    :name: pymssql
    :dbapi: pymssql
    :connectstring: mssql+pymssql://<username>:<password>@<freetds_name>/?charset=utf8

pymssql is a Python module that provides a Python DBAPI interface around
`FreeTDS <https://www.freetds.org/>`_.

.. note::

    pymssql is currently not included in SQLAlchemy's continuous integration
    (CI) testing.

Modern versions of this driver worked very well with SQL Server and FreeTDS
from Linux and were highly recommended. However, pymssql is currently
unmaintained and has fallen behind the progress of the Microsoft ODBC driver in
its support for newer features of SQL Server. The latest official release of
pymssql at the time of this document is version 2.1.4 (August, 2018) and it
lacks support for:

1. table-valued parameters (TVPs),
2. ``datetimeoffset`` columns using timezone-aware ``datetime`` objects
   (values are sent and retrieved as strings), and
3. encrypted connections (e.g., to Azure SQL), when pymssql is installed from
   the pre-built wheels. Support for encrypted connections requires building
   pymssql from source, which can be a nuisance, especially under Windows.

The above features are all supported by mssql+pyodbc when using Microsoft's
ODBC Driver for SQL Server (msodbcsql), which is now available for Windows,
(several flavors of) Linux, and macOS.


"""  # noqa
import re

from .base import MSDialect
from .base import MSIdentifierPreparer
from ... import processors
from ... import types as sqltypes
from ... import util


class _MSNumeric_pymssql(sqltypes.Numeric):
    def result_processor(self, dialect, type_):
        if not self.asdecimal:
            return processors.to_float
        else:
            return sqltypes.Numeric.result_processor(self, dialect, type_)


class MSIdentifierPreparer_pymssql(MSIdentifierPreparer):
    def __init__(self, dialect):
        super(MSIdentifierPreparer_pymssql, self).__init__(dialect)
        # pymssql has the very unusual behavior that it uses pyformat
        # yet does not require that percent signs be doubled
        self._double_percents = False


class MSDialect_pymssql(MSDialect):
    supports_statement_cache = True
    supports_native_decimal = True
    driver = "pymssql"

    preparer = MSIdentifierPreparer_pymssql

    colspecs = util.update_copy(
        MSDialect.colspecs,
        {sqltypes.Numeric: _MSNumeric_pymssql, sqltypes.Float: sqltypes.Float},
    )

    @classmethod
    def dbapi(cls):
        module = __import__("pymssql")
        # pymmsql < 2.1.1 doesn't have a Binary method.  we use string
        client_ver = tuple(int(x) for x in module.__version__.split("."))
        if client_ver < (2, 1, 1):
            # TODO: monkeypatching here is less than ideal
            module.Binary = lambda x: x if hasattr(x, "decode") else str(x)

        if client_ver < (1,):
            util.warn(
                "The pymssql dialect expects at least "
                "the 1.0 series of the pymssql DBAPI."
            )
        return module

    def _get_server_version_info(self, connection):
        vers = connection.exec_driver_sql("select @@version").scalar()
        m = re.match(r"Microsoft .*? - (\d+)\.(\d+)\.(\d+)\.(\d+)", vers)
        if m:
            return tuple(int(x) for x in m.group(1, 2, 3, 4))
        else:
            return None

    def create_connect_args(self, url):
        opts = url.translate_connect_args(username="user")
        opts.update(url.query)
        port = opts.pop("port", None)
        if port and "host" in opts:
            opts["host"] = "%s:%s" % (opts["host"], port)
        return [[], opts]

    def is_disconnect(self, e, connection, cursor):
        for msg in (
            "Adaptive Server connection timed out",
            "Net-Lib error during Connection reset by peer",
            "message 20003",  # connection timeout
            "Error 10054",
            "Not connected to any MS SQL server",
            "Connection is closed",
            "message 20006",  # Write to the server failed
            "message 20017",  # Unexpected EOF from the server
            "message 20047",  # DBPROCESS is dead or not enabled
        ):
            if msg in str(e):
                return True
        else:
            return False

    def set_isolation_level(self, connection, level):
        if level == "AUTOCOMMIT":
            connection.autocommit(True)
        else:
            connection.autocommit(False)
            super(MSDialect_pymssql, self).set_isolation_level(
                connection, level
            )


dialect = MSDialect_pymssql
