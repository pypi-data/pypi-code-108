"""
The ExSql view performs SQL queries directly against the
database. It can be used to perform high performance reads
or writes that are otherwise not allowed by Sage's validation
(caveat emptor).
"""
import re
from contextlib import contextmanager
from datetime import datetime

from extools.view import ExView, exview
from extools.view.errors import ExViewRecordDoesNotExist
from extools.message import logger_for_module

ERR_BAD_SQL = 110
ERR_RECORD_NOT_FOUND = 127


SQL_SERVER_ESCAPE_MAP = (
            ("\\\\", "\\\\\\\\"),
            ("/", "\\/"),
            ("'", "''"),
            ('"', '\\"')
)

def sql_escape(term):
    """Escape an SQL string for TSQL server (double quoted).

    The following terms are escaped:

    - ``\`` -> ``\\``
    - ``'`` -> ``''``
    - ``"`` -> ``\"``
    - ``/`` -> ``\/``

    :param term: the string to escape
    :type term: str
    :returns: TSQL escaped string
    :rtype: str

    .. code-block:: python

        query = "SELECT * from TABLE WHERE SHOW = '{showname}'"
        showname = sql_escape("Bob's Burgers") # -> "Bob''s Burgers"
        try:
            with exsql_result(query.format(showname=showname)) as result:
                return result.get("NETWORK")
        except ExViewRecordDoesNotExist:
            showMessageBox("No such show!")
        except ExSqlError:
            showMessageBox("Table or field do not exist.")
        except ExViewError:
            showMessageBox("An error occurred in the view.")

    """
    for match, replace in SQL_SERVER_ESCAPE_MAP:
        term = re.sub(match, replace, term)
    return term

@contextmanager
def exsql_result(query):
    """Open an ``ExSql`` view, executes a query, and yield the results.

    :param query: SQL query to execute.
    :type query: str
    :yields: ExSql
    :rtype: None
    :raises: :py:class:`extools.view.errors.ExSqlError`,
             :py:class:`extools.view.errors.ExViewError`

    .. code-block:: python

        query = ("SELECT ITEM FROM OEORDD WHERE "
                 "ORDUNIQ = {} AND LINENUM = {}".format(
                        234634, 2))
        try:
            with exsql_result(query) as res:
                item = res.get("ITEM")
        except ExSqlError as e:
            # Handle an SQL fail
        except ExViewError as e:
            # Handle a view layer fail
    """

    exs = ExSql()
    try:
        exs.query(query)
        if exs.fetch():
            yield exs
        else:
            raise ExViewRecordDoesNotExist(exs.rotoid, 'sql_query')
    finally:
        exs.close()

@contextmanager
def exsql():
    """Open an ``ExSql`` view and yield it.

    :yields: ExSql
    :rtype: None
    :raises: ExSqlError, ExViewError

    .. code-block:: python

        try:
            with exsql() as exs:
                exs.query("SELECT ITEM FROM OEORDD WHERE "
                          "ORDUNIQ = {} AND LINENUM = {}".format(
                                234634, 2))
                exs.fetch()
                item = exs.get("ITEM")
        except ExSqlError as e:
            # Handle an SQL fail
        except ExViewError as e:
            # Handle a view layer fail
    """
    exs = ExSql()
    try:
        yield exs
    except:
        exs.close()
        raise

class ExSql(ExView):
    """A class for working with the CS0120 view."""

    CSQL_VIEWID = "CS0120"

    def __init__(self):
        super().__init__(self.CSQL_VIEWID, seek_to=None)

    def query(self, query):
        """Perform an SQL query and return the view.

        :param query: an SQL query to execute.
        :type query: str
        :returns: view with the first result fetched.
        :rtype: ExView
        :raises: :py:class:`extools.view.errors.ExSqlError`,
                 :py:class:`extools.view.errors.ExViewError`


        If you only need to execute a query, consider using a
        context manager like :py:meth:`extools.view.exsql.exsql` or
        :py:meth:`extools.view.exsql.exsql_result`.

        .. code-block:: python

            try:
                exs = ExSql()
                result = exs.query("SELECT ITEM FROM OEORDD WHERE "
                                   "ORDUNIQ = {} AND LINENUM = {}".format(
                                        234634, 2))
                if exs.fetch():
                    item = result.get("ITEM")
                else:
                    # Handle record doesn't exist
            except ExSqlError as e:
                # Handle an SQL fail
            except ExViewError as e:
                # Handle a view layer fail
        """

        self.recordClear()
        return self.browse(query)

    def query_results(self, query):
        """Perform a query and yield the resulting records one at a time.

        :param query: an SQL query to execute.
        :type query: str
        :yields: ExView
        :returns: None
        :raises: :py:class:`extools.view.errors.ExSqlError`,
                 :py:class:`extools.view.errors.ExViewError`
        """

        result = self.query(query)
        while result.fetch():
            yield result

    def get(self, field, _type=-1, size=-1, precision=-1):
        """Get a field from view.

        Overrides the default get to skip verification that the field exists.
        """

        return super().get(field, _type, size, precision, verify=False)

    @classmethod
    def record_count(cls, table):
        """Get the total number of records from a table.

        :param table: name of the table to count records in.
        :returns: record count
        :rtype: int
        :raises: :py:class:`extools.view.errors.ExSqlError`,
                 :py:class:`extools.view.errors.ExViewError`
        """

        query = "SELECT COUNT(*) AS result FROM {}".format(table)
        with exsql_result(query) as result:
            return result.get("result")


def insert_optional_field(table, keys, user, org, field, value):

    query = """
            INSERT INTO {table}
                ({keys}, OPTFIELD, VALUE,
                 SWSET, AUDTDATE, AUDTTIME, AUDTUSER,
                 AUDTORG, TYPE, LENGTH, DECIMALS,
                 ALLOWNULL, VALIDATE)
                 VALUES
                 ({key_values}, '{field}', '{value}',
                 1, {date}, {time}, '{user}', '{org}',
                 {type}, {length}, {decimals}, {null},
                 {validate})
            """

    date = datetime.now().strftime("%Y%m%d")
    time = datetime.now().strftime("%H%M%S0")

    with exview("CS0011", seek_to={"OPTFIELD": field}) as optf:
        q = query.format(
                table=table,
                keys=", ".join(sorted(keys.keys())),
                key_values=",".join([str(keys[k]) for k in sorted(keys)]),
                field=field, value=value, date=date, time=time,
                user=user, org=org, type=optf.get("TYPE"),
                length=optf.get("LENGTH"), decimals=optf.get("DECIMALS"),
                null=optf.get("ALLOWNULL"), validate=optf.get("VALIDATE"))
        with exsql() as exs:
            exs.query(q)
            exs.fetch()

def update_optional_field(table, keys, user, org, field, value):

    query = """
            UPDATE {table}
            SET VALUE = '{value}', AUDTUSER = '{user}',
                AUDTDATE = {date}, AUDTTIME = {time},
                AUDTORG = '{org}'
            WHERE {where} AND OPTFIELD = '{field}'
            """

    date = datetime.now().strftime("%Y%m%d")
    time = datetime.now().strftime("%H%M%S0")

    where = ["{} = {}".format(f, v) for f, v in keys.items()]
    q = query.format(
            table=table,
            where=" AND ".join(where),
            field=field, value=value, date=date, time=time,
            user=user, org=org)
    with exsql() as exs:
        exs.query(q)
        exs.fetch()

def columns_for_table(table):
    log = logger_for_module('extools', box=None)
    query = """select CAST(COLUMN_NAME AS CHAR) AS COL
             from information_schema.columns 
             where table_name = '{}'
             order by ordinal_position""".format(table)
    cols = []
    with exsql() as exs:
        exs.query(query)
        while exs.fetch():
            cols.append(exs.get("COL", 1))
    return cols